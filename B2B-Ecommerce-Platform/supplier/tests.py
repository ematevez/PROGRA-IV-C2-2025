from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import resolve, reverse_lazy
from django.test import Client


# from apps
from supplier import views as SupplierViews
from supplier import models
from auth_app.models import Supplier


class SupplierTest(TestCase):
    def test_models_created(self):
        # supplier
        test_supplier = Supplier.objects.create(
            username="testuser", email="test@test.com", password="testUser123"
        )

        # store can exist in one location
        test_store = models.Store.objects.create(
            name="test store name", supplier=test_supplier
        )

        # test_store.location.add(test_location)
        # self.assertIn(test_store, models.Store.objects.filter(location=test_location))

        # product category
        test_category = models.ProductCategory.objects.create(
            name="Fashion",
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
        )

        # product subcategories
        test_subcategory = models.ProductSubCategory.objects.create(
            name="men fashion",
            category=test_category,
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
        )

        test_product = models.Product.objects.create(
            name="product name",
            description="product description",
            sub_category=test_subcategory,
            price="200.0",
            currency="USD",
        )

        # category product count increases
        self.assertEqual(test_category.product_count, 1)

        test_product.store.add(test_store)
        self.assertIn(test_product, models.Product.objects.filter(store=test_store))

        # add images
        test_product_image = models.ProductImage(
            product=test_product,
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
        )
        test_product_image.save()

        # suppliers can create services, on which buyer can make contracts
        test_supplier_service = models.Service.objects.create(
            supplier=test_supplier,
            name="Represention",
            description="Test description",
            price="200.0",
            currency="USD",
        )

        # confirm product images are deleted
        test_product.delete()
        self.assertFalse(models.ProductImage.objects.filter(id=test_product_image.id))


class TestAppRequests(TestCase):
    fixtures = [
        "supplier.json",
        "profile.json",
        "supplier_fixtures.json",
    ]

    def setUp(self):
        self.client = Client()

        self.test_product = models.Product.objects.all().first()
        self.test_category = models.ProductCategory.objects.all().first()
        self.test_store = models.Store.objects.all().first()
        self.test_subcategory = models.ProductSubCategory.objects.all().first()
        return super().setUp()

    def test_app_urls(self):
        # Products
        products_found = resolve(reverse_lazy("supplier:products"))
        self.assertEqual(
            products_found.func.__name__,
            SupplierViews.ProductListView.as_view().__name__,
        )

        # Product detail
        products_found = resolve(
            reverse_lazy(
                "supplier:product-detail", kwargs={"slug": self.test_product.slug}
            )
        )
        self.assertEqual(
            products_found.func.__name__,
            SupplierViews.ProductDetailView.as_view().__name__,
        )

        # Categories
        category_found = resolve(reverse_lazy("supplier:category-list"))
        self.assertEqual(
            category_found.func.__name__,
            SupplierViews.CategoryListView.as_view().__name__,
        )

        # Category detail
        categories_found = resolve(
            reverse_lazy(
                "supplier:category-detail", kwargs={"slug": self.test_category.slug}
            )
        )
        self.assertEqual(
            categories_found.func.__name__,
            SupplierViews.CategoryDetailView.as_view().__name__,
        )

        # Sub Category detail
        sub_categories_found = resolve(
            reverse_lazy(
                "supplier:subcategory-detail",
                kwargs={
                    "category_slug": self.test_category.slug,
                    "sub_category_slug": self.test_subcategory.slug,
                },
            )
        )
        self.assertEqual(
            sub_categories_found.func.__name__,
            SupplierViews.SubCategoryDetailView.as_view().__name__,
        )

        # Store detail
        stores_found = resolve(
            reverse_lazy("supplier:store-detail", args=[self.test_store.slug])
        )
        self.assertEqual(
            stores_found.func.__name__, SupplierViews.StoreDetailView.as_view().__name__
        )

    def test_product_list_page(self):

        # a request is made to that base app
        response = self.client.get(reverse_lazy("supplier:products"))

        # template used
        self.assertTemplateUsed(response, "supplier/product_list.html")

        # view context
        view_context = ["view_name", "product_categories", "product_list"]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        # self.assertIn("sub_category", response.context.get("object_list")[0].keys())

    def test_product_detail_page(self):

        # a request is made to that base app
        response = self.client.get(
            reverse_lazy("supplier:product-detail", args=[self.test_product.slug])
        )
        self.assertEqual(response.status_code, 200)

        # # template used
        self.assertTemplateUsed(response, "supplier/product_detail.html")

        # # view context
        view_context = [
            "view_name",
            "product_categories",
            "product",
            "related_products",
            "product_images",
        ]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        self.assertEqual(response.context.get("product").name, self.test_product.name)

    def test_category_list_view(self):

        # a request is made to that base app
        response = self.client.get(reverse_lazy("supplier:category-list"))

        # template used
        self.assertTemplateUsed(response, "supplier/productcategory_list.html")

        self.assertEqual("Categories", response.context.get("view_name"))

        self.assertIn(
            self.test_category,
            [
                category.get("category")
                for category in response.context.get("object_list")
            ],
        )

    def test_category_detail_view(self):

        response = self.client.get(
            reverse_lazy("supplier:category-detail", args=[self.test_category.slug])
        )
        self.assertEqual(response.status_code, 200)

        # # template used
        self.assertTemplateUsed(response, "supplier/productcategory_detail.html")

        # # view context
        view_context = [
            "view_name",
            "products",
            "product_count",
            "other_categories",
        ]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        self.assertEqual(
            response.context.get("productcategory").name, self.test_category.name
        )

    def test_subcategory_detail_view(self):
        response = self.client.get(
            reverse_lazy(
                "supplier:subcategory-detail",
                kwargs={
                    "category_slug": self.test_category.slug,
                    "sub_category_slug": self.test_subcategory.slug,
                },
            )
        )
        self.assertEqual(response.status_code, 200)

        # # template used
        self.assertTemplateUsed(response, "supplier/products.html")

        view_context = [
            "view_name",
            "products",
            "related_subcategories",
        ]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

    def test_store_detail_view(self):

        response = self.client.get(
            reverse_lazy("supplier:store-detail", args=[self.test_store.slug])
        )

        self.assertEqual(response.status_code, 200)

        # template used
        self.assertTemplateUsed(response, "supplier/store_detail.html")

        # view context
        view_context = [
            "view_name",
            "showrooms",
            "products",
            "product_count",
            "stores",
        ]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        self.assertEqual(response.context.get("object"), self.test_store)
