from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# python
import datetime
from dateutil.relativedelta import relativedelta
import string
import uuid

# apps
from auth_app.models import Supplier, Buyer
from supplier.models import Service
from manager.models import Advert

from manager import tasks as ManagerTasks

class ModelWithNameBasedSlug(models.Model):

    class Meta:
        abstract = True

    name = models.CharField(_("Name"), max_length=256)
    slug = models.SlugField(
        _("Safe Url"),
        unique=True,
        blank=True,
        null=True,
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:50]

        self.name = self.name

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

class MembershipGroup(ModelWithNameBasedSlug):
    
    # group_types = (
    #     ("SHOWROOMS", "SHOWROOMS"),
    #     ("LOCAL", "LOCAL"),
    # )
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True
    )
    # group_type = models.CharField(_("Type"), choices=group_types, max_length=256, blank=True, null=True)

class MembershipPlan(ModelWithNameBasedSlug):
    group = models.ForeignKey(to=MembershipGroup, on_delete=models.CASCADE)
    features = models.ManyToManyField(to="Feature", related_name="features_list")
    description = models.TextField(
        _("Description"),
        blank=True,
        null=True
    )
    def __str__(self) -> str:
        return f"{self.group} - {self.name}"

class Feature(models.Model):
    custom_id = models.CharField(_("id"), max_length=256, blank=True, null=True)
    name = models.CharField(_("Name"), max_length=256, blank=True, null=True)
    price = models.CharField(_("price"), max_length=256, blank=True, null=True)

    description = models.CharField(_("description"), max_length=256, blank=True, null=True)
    billing_frequency = models.CharField(_("billing_frequency"), max_length=256, blank=True, null=True)
    currency_iso_code = models.CharField(_("Currency"), max_length=256, blank=True, null=True)
    interval_unit = models.CharField(_("Duration"), max_length=256)
    status = models.CharField(_("Status"), max_length=256)

    has_trial = models.BooleanField("Has Trial Period", default=False)
    trial_period = models.CharField(_("Trial Period"), max_length=256, blank=True, null=True)
    trial_period_count = models.CharField(_("Trial Period Count"), max_length=256, blank=True, null=True)
    paypal_id = models.CharField(_("paypal_id"), max_length=256, blank=True, null=True)

    def get_duration(self):
        if self.billing_frequency == "1":
            return _("Per Month")
        elif self.billing_frequency == "6":
            return _("Per 6 Months")
        elif self.billing_frequency == "12":
            return _("Per Year")

    def save(self, *args, **kwargs):
        self.duration = self.get_duration()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} - {self.price}"

    def to_braintree_json(self):
        obj = {
            "id": self.custom_id,
            "name": self.name,
            "description": self.description,
            "billing_frequency": self.billing_frequency,
            "currency_iso_code": self.currency_iso_code,
            "price": self.price
        }
        return obj

    def to_paypal_json(self, product):
        obj = {
            "product_id": f"{product.custom_id}",
            "name": f"{self.name}",
            "description": f"{self.description}",
            "status": f"{self.status}",
            "billing_cycles": [
                {
                    "frequency": {
                    "interval_unit": "YEAR" if self.billing_frequency == "12" else self.interval_unit,
                    "interval_count": "1" if self.billing_frequency == "12" else self.billing_frequency,
                    },
                    "tenure_type": "REGULAR",
                    "sequence": 2 if self.has_trial else 1,
                    "total_cycles": 0,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": f"{self.price}",
                        "currency_code": f"{self.currency_iso_code}",
                    }
                    }
                }
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee": {
                    "value": "0",
                    "currency_code": f"{self.currency_iso_code}",
                },
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 3
            },
            "taxes": {
                "percentage": "0",
                "inclusive": False
            }
        }

        if self.has_trial:
            obj["billing_cycles"].append(
                {
                    "frequency": {
                        "interval_unit": self.trial_period,
                        "interval_count": self.trial_period_count
                    },
                    "tenure_type": "TRIAL",
                    "sequence": 1,
                    "total_cycles": 1,
                    "pricing_scheme": {
                    "fixed_price": {
                        "value": "0",
                        "currency_code": f"{self.currency_iso_code}",
                        }
                    }
                }
            )

        return obj

class ActiveMembership(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(status=True)


class Membership(models.Model):
    objects = models.Manager()
    active = ActiveMembership()
    
    group_types = (
        ("BRAINTREE CARD", "BRAINTREE CARD"),
        ("PAYPAL", "PAYPAL"),
    )
    membership_type = models.CharField(_("Type"), choices=group_types, max_length=256, blank=True, null=True)
    client = models.ForeignKey(to=Supplier, on_delete=models.CASCADE, blank=True, null=True)

    feature = models.ForeignKey(to=Feature, on_delete=models.CASCADE, related_name="feature", blank=True, null=True)
    previous_feature = models.ForeignKey(to=Feature, on_delete=models.CASCADE, blank=True, null=True, related_name="previous_pricing")
    upgrading_to = models.ForeignKey(to=Feature, on_delete=models.CASCADE, blank=True, null=True, related_name="upgrading_to")
    start_date = models.DateField(_("Subscription Start Date"), default=datetime.date.today)
    expiry_date = models.DateField(_("Subscription Expiry Date"), blank=True, null=True)
    status = models.BooleanField(_("Active"), default=False)
    payment_completed = models.BooleanField(_("Payment Completed"), default=False)

class CardPayment(models.Model):
    subscription = models.OneToOneField(to="BraintreeSubscription", on_delete=models.CASCADE)
    card_token = models.CharField(_("card_token"), max_length=256)
    card_last_4 = models.CharField(_("card_last_4"), max_length=256)
    card_type = models.CharField(_("card_type"), max_length=256)
    card_expiration_month = models.CharField(_("card_expiration_month"), max_length=256)
    card_expiration_year = models.CharField(_("card_expiration_year"), max_length=256)
    card_customer_location = models.CharField(_("card_customer_location"), max_length=256)
    card_issuing_bank = models.CharField(_("card_issuing_bank"), max_length=256)


class BraintreeSubscription(models.Model):    
    class Meta:
        ordering = ['-id']

    membership = models.OneToOneField(to=Membership, on_delete=models.CASCADE, related_name="braintree_membership", blank=True, null=True)
    subscription_id = models.CharField(_("current_billing_cycle"), max_length=256, blank=True, null=True)
    payment_method = models.CharField(_("Payment Method"), max_length=20, blank=True, null=True)

    current_billing_cycle = models.CharField(_("current_billing_cycle"), max_length=256, blank=True, null=True)
    days_past_due = models.CharField(_("days_past_due"), max_length=256, blank=True, null=True)
    next_billing_date = models.CharField(_("next_billing_date"), max_length=256, blank=True, null=True)
    payment_method_token = models.CharField(_("payment_method_token"), max_length=256, blank=True, null=True)
    
    created_on = models.DateField(_("Created on"), default=timezone.now)



class PaypalSubscription(models.Model):
    membership = models.OneToOneField(to=Membership, on_delete=models.CASCADE, related_name="paypal_membership", blank=True, null=True)
    order_key = models.CharField(_("Order key"), max_length=256, blank=True, null=True)

    created_on = models.DateField(_("Created on"), default=datetime.date.today)

class PaypalProduct(models.Model):
    custom_id = models.CharField(_("Product Id"), max_length=256, null=True, blank=True)
    name = models.CharField(_("Name"), max_length=256)
    ProductType = models.CharField(_("Type"), max_length=256, default="Service")
    description = models.TextField(_("Description"), max_length=256)

    def __str__(self):
        return f"{self.name}"

    def save(self):
        if not self.custom_id:
            self.custom_id = "-".join(self.name.split(" "))
        super().save()

    def toJSON(self):
        obj = {
            "id" : self.custom_id,
            "name" : self.name,
            "service" : self.ProductType,
            "description" : self.description,
        }
        return json.dumps(obj)

class ModeOfPayment(ModelWithNameBasedSlug):
    transaction_count = models.IntegerField(_("Number of transactions"), default=0)

class MembershipReceipt(models.Model):
    method = models.CharField(_("Payment Method"), max_length=20)
    plan_id = models.CharField(_("Plan Id"), max_length=30)
    client = models.ForeignKey(to=Supplier, on_delete=models.CASCADE)
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def __str__(self) -> str:
        return f"User: {self.payment_id}"


class Contract(models.Model):
    ref_no = models.CharField(
        _("Reference Number"), null=True, blank=True, unique=True, max_length=15
    )
    supplier = models.ForeignKey(
        to=Supplier, on_delete=models.CASCADE, related_name="supplier"
    )
    buyer = models.ForeignKey(to=Buyer, on_delete=models.CASCADE, related_name="buyer")

    service = models.ForeignKey(
        to=Service, on_delete=models.CASCADE, related_name="supplier_service"
    )

    is_complete = models.BooleanField(_("Contract completed"), default=False)
    is_accepted = models.BooleanField(_("Contract accepted"), default=False)
    payment_made = models.BooleanField(_("Contract payment made"), default=False)

    start_date = models.DateField(_("start date"), default=timezone.now)
    end_date = models.DateField(_("end date"), null=True, blank=True)
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.ref_no = str(uuid.uuid4())[:15].replace("-", "")

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Supplier: {self.supplier.username}, Buyer: {self.buyer.username}"

class ContractReceipt(models.Model):
    contract = models.ForeignKey(
        to=Contract,
        on_delete=models.CASCADE,
    )
    mode_of_payment = models.ForeignKey(to=ModeOfPayment, on_delete=models.CASCADE)
    address = models.CharField(_("Address"), max_length=256)
    payment_id = models.CharField(_("Payment Id"), max_length=256)
    amount_paid = models.DecimalField(
        _("Total Amount Paid"), decimal_places=2, max_digits=12
    )
    currency = models.CharField(_("Currency"), max_length=6)

    def __str__(self) -> str:
        return f"User: {self.payment_id}"

class AdvertPaymentReceipt:
    advert_payment = models.ForeignKey(
        to=Advert,
        on_delete=models.CASCADE,
    )
    mode_of_payment = models.ForeignKey(to=ModeOfPayment, on_delete=models.CASCADE)
    address = models.CharField(_("Address"), max_length=256)
    payment_id = models.CharField(_("Payment Id"), max_length=256)
    amount_paid = models.DecimalField(
        _("Total Amount Paid"), decimal_places=2, max_digits=12
    )
    currency = models.CharField(_("Currency"), max_length=6)

    def __str__(self) -> str:
        return f"User: {self.payment_id}"


# @receiver(post_save, sender=MembershipGroup)
# def translate(sender, instance, *args, **kwargs):
#     fields = ("name", "description")
#     ManagerTasks.make_manager_model_translations.delay(fields, instance.pk, instance.__class__.__name__, "payment")

# @receiver(post_save, sender=MembershipPlan)
# def translate(sender, instance, *args, **kwargs):
#     fields = ("name", "description")
#     ManagerTasks.make_manager_model_translations.delay(fields, instance.pk, instance.__class__.__name__, "payment")