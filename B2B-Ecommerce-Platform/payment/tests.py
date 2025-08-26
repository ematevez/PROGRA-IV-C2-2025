from django.test import TestCase

# python
import datetime
from dateutil.relativedelta import relativedelta

# from apps
from payment import models
from auth_app.models import Buyer, Supplier


class PaymentTest(TestCase):
    def test_models_created(self):
        test_buyer = Buyer.objects.create(
            username="testbuyer", email="test@test.com", password="testUser123"
        )
        test_supplier = Supplier.objects.create(
            username="testsupplier", email="test@test.com", password="testUser123"
        )

        test_membership_plan = models.MembershipPlan.objects.create(
            name="Gold",
            price=100,
            currency="USD",
            description="the description",
        )

        test_membership = models.Membership.objects.create(
            supplier=test_supplier, plan=test_membership_plan, duration="Monthly"
        )

        self.assertEqual(
            test_membership.expiry_date,
            (datetime.date.today() + relativedelta(months=1)).strftime("%Y-%m-%d"),
        )

        test_mode_of_payment = models.ModeOfPayment.objects.create(name="Paypal")

        # membership payment receipt
        test_membership_receipt = models.MembershipReceipt.objects.create(
            membership=test_membership,
            model_of_payment=test_mode_of_payment,
            address="Kampala",
            payment_id="23f29g29092v",
            amount_paid="422.000",
            currency="USD",
        )

        self.assertAlmostEquals(test_mode_of_payment.transaction_count, 1)

        # supplier service
        test_supplier_service = models.Service.objects.create(
            supplier=test_supplier,
            name="Represention",
            description="Test description",
            price="200.0",
            currency="USD",
        )

        # contracts
        test_contract = models.Contract.objects.create(
            supplier=test_supplier,
            buyer=test_buyer,
            service=test_supplier_service,
        )

        test_contract_reciept = models.ContractReceipt.objects.create(
            contract=test_contract,
            model_of_payment=test_mode_of_payment,
            address="Kampala",
            payment_id="23f29g29092v",
            amount_paid="422.000",
            currency="USD",
        )
