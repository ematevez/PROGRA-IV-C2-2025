from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

# apps
from auth_app import models
from auth_app.models import User


class AuthAppTest(TestCase):
    def test_models_created(self):
        # test the parent user class
        # this is that the admin will be using

        test_admin_user = models.User.objects.create_user(
            username="phillip", password="MAke390"
        )

        self.assertTrue(test_admin_user.is_superuser)

        # test Supplier

        test_supplier_user = models.Supplier.objects.create_user(
            username="peter", password="MAke390"
        )
        self.assertFalse(test_supplier_user.is_superuser)

        test_supplier_user_profile = models.ClientProfile.objects.create(
            user=test_supplier_user,
            country_code="256",
            country="Uganda",
            city="Uganda",
            mobile_user="0782047612",
            vat_number=114325,
            legal_etity_identifier="vnvio32o",
        )
        self.assertAlmostEquals(test_supplier_user.profile, test_supplier_user_profile)

        # test Buyer
        test_buyer_user = models.Buyer.objects.create_user(
            username="alex", password="MAke390"
        )
        self.assertFalse(test_buyer_user.is_superuser)

        test_buyer_user_profile = models.ClientProfile.objects.create(
            user=test_buyer_user,
            country_code="256",
            country="Uganda",
            city="Uganda",
            mobile_user="0782047612",
            vat_number=114325,
            legal_etity_identifier="vnvio32o",
        )
        self.assertAlmostEquals(test_buyer_user.profile, test_buyer_user_profile)

        # user has to activate his activate via his email
        self.assertFalse(test_buyer_user.is_active)

        # support

        test_support_user = models.Support.objects.create_user(
            username="mark", password="MAke390"
        )
        self.assertAlmostEquals(test_support_user.account_type, "SUPPORT")
