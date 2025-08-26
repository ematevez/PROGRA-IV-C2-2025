# django
from django.db import models
from django.utils import timezone
import datetime
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Q
from django.core.validators import MinValueValidator

# python
import os
import uuid
import string

# apps
from auth_app.models import Supplier, Buyer, ClientProfile, User
from buyer import models as BuyerModels
from supplier import tasks as SupplierTasks

# utility functions
def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    # filename = "%s-%s.%s" % (instance.slug, uuid.uuid4(), ext)
    filename = f"{instance.slug}-{uuid.uuid4()}"[:50] + f".{ext}"
    return os.path.join(f"{instance.__class__.__name__}/images/", filename)


# utility functions
def get_video_path(instance, filename):
    ext = filename.split(".")[-1]
    # filename = "%s-%s.%s" % (instance.slug, uuid.uuid4(), ext)
    filename = f"{instance.slug}-{uuid.uuid4()}"[:50] + f".{ext}"
    return os.path.join(f"{instance.__class__.__name__}/video/", filename)

# global model managers

class VerifiedManager(models.Manager):
    def get_queryset(self):
        # Override the default queryset to exclude inactive items
        return super().get_queryset().filter(is_verified=True)


class AdminListManager(models.Manager):
    def get_queryset(self):
        # Override the default queryset to exclude inactive items
        return super().get_queryset().all()

class Store(models.Model):
    objects = VerifiedManager()
    admin_list = AdminListManager()

    name = models.CharField(_("Store Name"), max_length=256)
    supplier = models.ForeignKey(
        to=Supplier,
        on_delete=models.CASCADE,
    )
    # location = models.ManyToManyField(
    #     to=Location,
    #     related_name='store_locations',
    #     default=None
    # )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=200
    )

    image = models.FileField(
        verbose_name=_("Service Image"),
        upload_to=get_file_path,
        default="test/django.png",
    )
    is_verified = models.BooleanField(_("Verified by Admin"), default=True)
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        self.name = self.name

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"


#======================================= Product =======================================
class ProductCategory(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    product_count = models.IntegerField(_("Number of products"), default=0)
    image = models.FileField(
        verbose_name=_("Image"),
        upload_to=get_file_path,
        default="test/django.png",
    )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=200
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        self.name = self.name

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"


class ProductSubCategory(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    category = models.ForeignKey(to=ProductCategory, on_delete=models.CASCADE)
    image = models.FileField(
        verbose_name=_("Image"),
        upload_to=get_file_path,
        default="test/django.png",
    )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=200
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]

        self.name = self.name

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name}"

class Product(models.Model):
    objects = VerifiedManager()
    admin_list = AdminListManager()
    class Meta:
        ordering = ["-id"]

    name = models.CharField(_("Name"), max_length=256)
    description = models.TextField(
        _("Description"),
    )
    # for easy querying supplier attribute has been added
    business = models.ForeignKey(
        to=ClientProfile,
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    # can be in many stores
    store = models.ManyToManyField(to=Store, related_name="store_product", blank=True)
    category = models.ForeignKey(
        to=ProductCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    sub_category = models.ForeignKey(
        to=ProductSubCategory,
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=200
    )
    currency = models.CharField(_("Currency"), max_length=6, blank=True, null=True)
    price = models.DecimalField(_("Price"), decimal_places=2, max_digits=12, blank=True, null=True)
    discount = models.DecimalField(_("Discount as a Percentage"), decimal_places=2, max_digits=3, blank=True, null=True)
    stock = models.IntegerField(_("stock"), blank=True, null=True)
    is_verified = models.BooleanField(_("Verified by Admin"), default=True)
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.slug or slugify(self.name) not in self.slug:
            self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:200]
        self.category = self.sub_category.category

        self.name = self.name

        super().save(*args, **kwargs)

    def sell_made(self, items_sold):
        if self.stock > 0 and items_sold >= self.stock:
            self.stock = self.stock - int(items_sold)
            self.save()
            SupplierTasks.inventory_check.delay(self.pk)
        else:
            raise ValueError(_('Items sold are more than available stock'))

    @property
    def supplier(self):
        if not self.store.all():
            return self.business
        return self.store.all().first().supplier.profile
        
    @property
    def stores(self):
        if not self.store.all():
            return None
        return self.store.all()

    def __str__(self) -> str:
        return f"{self.name} {self.supplier}"



class ProductImage(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    image = models.FileField(
        verbose_name=_("Image"),
        upload_to=get_file_path,
    )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=100
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.product.name[:10]}-{uuid.uuid4()}")[:50] + "-images"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.name}"

class ProductVideo(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    video = models.FileField(
        verbose_name=_("Video"),
        upload_to=get_video_path,
    )
    slug = models.SlugField(
        _("Safe Url"), unique=True, blank=True, null=True, max_length=100
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.product.name[:10]}-{uuid.uuid4()}")[:50] + "-videos"
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.name}"


class ProductTag(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"

class ProductColor(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"

class ProductMaterial(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"

        
class ProductPrice(models.Model):
    currency = models.CharField(_("Currency"), max_length=6)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    min_price = models.DecimalField(_("Min Price"), decimal_places=2, max_digits=12)
    max_price = models.DecimalField(_("Max Price"), decimal_places=2, max_digits=12)

    def save(self, *args, **kwargs):
        if not (self.product.currency or self.product.price):
            self.product.currency = self.currency
            self.product.price = self.min_price
            # self.product.save(update_fields=['currency', 'price'])
            self.product.save()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.currency}"
        
class ProductReview(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    business = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE)
    content = models.TextField(_("Review Context"), blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.name}"


#======================================= Product =======================================


#======================================= Order =======================================

class Order(models.Model):
    class Meta:
        ordering = ("-id","-updated_on")

    order_statuses = (
        (_("PENDING"), _("PENDING")),
        (_("VIEWED BY SUPPLER"), _("VIEWED BY SUPPLER")),
        (_("ACCEPTED BY SUPPLER"), _("ACCEPTED BY SUPPLER")),
        (_("IN DELIVERY"), _("IN DELIVERY")),
        (_("DELIVERED"), _("DELIVERED")),
        (_("REJECTED"), _("REJECTED")),
        (_("CANCELLED"), _("CANCELLED")),
        (_("COMPLETED"), _("COMPLETED")),
    )
    order_id = models.CharField(_("Order Id"), max_length=50, unique=True, blank=True, null=True)
    buyer = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE, related_name="buyer")
    supplier = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE, related_name="supplier")
    status = models.CharField(_("Order Status"), max_length=256, choices=order_statuses, default="PENDING")
    currency = models.CharField(_("Currency"), max_length=6, blank=True, null=True)
    total_price = models.DecimalField(_("Total Price"), decimal_places=2, max_digits=12, blank=True, null=True)
    agreed_price = models.DecimalField(_("Agreed Price"), decimal_places=2, max_digits=12, blank=True, null=True)
    paid_price = models.DecimalField(_("Paid Price"), decimal_places=2, max_digits=12, blank=True, null=True)
    discount = models.DecimalField(_("Discount as a Percentage"), decimal_places=2, max_digits=3, blank=True, null=True, default=0.00)
    is_complete = models.BooleanField(_("Completed"), default=True)
    accepted_on = models.DateField(_("Accepted on"), blank=True, null=True)
    delivery_date = models.DateField(_("Delivery Date"), blank=True, null=True) 
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)

    def generateOrderId(self):
        pretext = "FODR"

        today = datetime.datetime.now()

        order_id = f"{pretext}{str(today.year)[2:]}{str(today.month)}{str(today.day)}{str(today.hour)}{str(today.minute)}{str(today.second)}"

        # check if id exists
        if Order.objects.filter(order_id=order_id):
            # if exists. regenerate
            order_id = f"{pretext}{str(today.year)[2:]}{str(today.month)}{str(today.day)}{str(today.hour)}{str(today.minute)}{str(today.second)}"

        return order_id

    def computeTotalPrice(self):
        # using set discounts
        if not self.agreed_price:
            return 0
        if not self.discount:
            self.discount = 0
            
        total_price = float(self.agreed_price) - ( float(self.agreed_price) * (self.discount / 100))

        # adding shipping taxings
        shipping_details = OrderShippingDetail.objects.filter(order = self)
        if shipping_details:
            shipping_tax = shipping_details.first().get_tax()
            total_price = total_price + (total_price * shipping_tax)

        return total_price

    def save(self, *args, **kwargs):

        def get_tax(self):
            pass
        if not self.order_id:
            self.order_id = self.generateOrderId()

        self.updated_on = datetime.datetime.now()

        # compute total price basing on taxes and charges
        self.total_price = self.computeTotalPrice()

        if self.is_complete and self.status != "COMPLETED":
            self.status = "COMPLETED"
        if self.status == "COMPLETED" and not self.is_complete:
            self.is_complete = True
        
        super(Order, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.order_id} - {self.supplier} - {self.buyer} - {self.status}"

class OrderProductVariation(models.Model):
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, null=True, blank=True)
    cart = models.ForeignKey(to=BuyerModels.Cart, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    price = models.ForeignKey(to=ProductPrice, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(to=ProductColor, on_delete=models.CASCADE, null=True, blank=True)
    material = models.ForeignKey(to=ProductMaterial, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(_("Quantity"), validators=[MinValueValidator(0)])
    min_total_price = models.DecimalField(_("Min Total Price"), decimal_places=2, max_digits=12, blank=True, null=True)
    max_total_price = models.DecimalField(_("Max Total Price"), decimal_places=2, max_digits=12, blank=True, null=True)

    def save(self, *args, **kwargs):
        if int(self.quantity) > 0 and self.price:
            self.min_total_price = int(self.quantity) * float(self.price.min_price)
            self.max_total_price = int(self.quantity) * float(self.price.max_price)
        
        super(OrderProductVariation, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.product}"

class OrderNote(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE)
    notes = models.TextField(
        _("Notes"),
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updated_on = datetime.datetime.now()
        
        super(OrderNote, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.order}"


class DeliveryCarrier(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    tax = models.DecimalField(_("Tax as a Percentage (00.00)"), decimal_places=2, max_digits=3, blank=True, null=True)
    delivery_period = models.IntegerField(_("Days of Delivery"), blank=True, null=True)
    active = models.BooleanField(_("Is Active"), default=True)
    
    def __str__(self) -> str:
        return f"{self.name}"

class OrderShippingDetail(models.Model):
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE)
    carrier = models.OneToOneField(to=DeliveryCarrier, on_delete=models.CASCADE, blank=True, null=True)
    address_1 = models.CharField(_("Shipping Address 1"), max_length=50, blank=True, null=True)
    address_2 = models.CharField(_("Shipping Address 1"), max_length=50, blank=True, null=True)
    # use busines contact information

    def get_tax(self):
        # returns a percentage ie 0.03 = 3%
        return int(self.carrier.tax) / 100


def get_chat_file_path(instance):
    ext = ".json"
    filename = instance.chat_id
    path = os.path.join(f"{settings.ORDERCHATFILES_DIR}/{filename}{ext}")
    return path

#======================================= Order =======================================


#======================================= WishList =======================================

class WishListProduct(models.Model):
    buyer = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

#======================================= WishList =======================================
class Service(models.Model):
    supplier = models.ForeignKey(
        to=Supplier,
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("Name"), max_length=256)
    description = models.TextField(
        _("Description"),
    )
    price = models.DecimalField(_("Price"), decimal_places=2, max_digits=13)
    currency = models.CharField(_("Currency"), max_length=7)
    contract_count = models.IntegerField(_("Number of contracts"), default=0)
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

class ServiceImage(models.Model):
    service = models.ForeignKey(to=Service, on_delete=models.CASCADE)
    image = models.ImageField(
        verbose_name=_("Service Image"),
        upload_to=get_file_path,
    )
    slug = models.SlugField(
        _("Safe Url"),
        unique=True,
        blank=True,
        null=True,
    )
    created_on = models.DateField(_("Created on"), default=timezone.now)

    def save(self, *args, **kwargs):
        self.slug = f"{slugify(self.service.name)}-{uuid.uuid4()}"[:50]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.service.name}"


class ServiceTag(models.Model):
    name = models.CharField(_("Name"), max_length=256)
    service = models.ForeignKey(to=Service, on_delete=models.CASCADE)
    slug = models.SlugField(
        _("Safe Url"),
        unique=True,
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}{uuid.uuid4()}")[:50]

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.service.name}"

        
# SIGNALS
@receiver(post_save, sender=Product)
def on_product_save(sender, instance, **kwargs):
    product_sub_category = instance.sub_category
    # category product count increases
    product_sub_category.category.product_count += 1
    product_sub_category.category.save(update_fields=['product_count'])


@receiver(post_delete, sender=Product)
def delete_product(sender, instance, *args, **kwargs):
    images = ProductImage.objects.filter(product=instance)
    for image in images:
        image.delete()

    videos = ProductVideo.objects.filter(product=instance)
    for video in videos:
        video.delete()

    for record in ProductTag.objects.filter(product=instance):
        record.delete()

    for record in ProductColor.objects.filter(product=instance):
        record.delete()

    for record in ProductMaterial.objects.filter(product=instance):
        record.delete()

    for record in ProductPrice.objects.filter(product=instance):
        record.delete()

    product_sub_category = instance.sub_category
    # category product count decreases
    product_sub_category.category.product_count -= 1
    product_sub_category.category.save(update_fields=['product_count'])


@receiver(post_delete, sender=Store)
def delete_store(sender, instance, *args, **kwargs):
    if instance.image and instance.image != "test/django.png":
        instance.image.delete()
