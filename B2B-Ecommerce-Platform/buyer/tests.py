# django
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

# apps
from buyer import models
from auth_app.models import Buyer
from supplier.models import Product, ProductCategory


class BuyerTest(TestCase):
    def test_models_created(self):
        # buyer
        test_buyer = Buyer.objects.create(
            username="testuser", email="test@test.com", password="testUser123"
        )

        # wishlist
        # when are user adds product to wishlist(expresses interest), the supplier is notified

        # product category
        test_category = ProductCategory.objects.create(
            name="Fashion",
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
        )

        test_product = Product.objects.create(
            name="product name",
            description="product description",
            category=test_category,
            price="200.0",
            currency="USD",
        )

        test_wishlist = models.WishList.objects.create(
            buyer=test_buyer, product=test_product
        )
