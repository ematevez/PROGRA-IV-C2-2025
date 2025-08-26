from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import resolve, reverse_lazy

# apps
from manager import models
from supplier.models import Store
from auth_app.models import User

from manager import views as ManagerViews


class ModelTest(TestCase):
    def test_models_created(self):
        # locations
        location_test = models.Location(
            name="UAE - Dubai",
        )

        location_test.save()

        # Service
        service_test = models.Service(
            name="Represention", description="Test description"
        )

        service_test.save()

        # service images

        # confirm mediaroot is set
        self.assertTrue(settings.MEDIA_URL)
        self.assertTrue(settings.MEDIA_ROOT)

        service_img_test = models.ServiceImage(
            service=service_test,
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
        )
        service_img_test.save()

        # showrooms

        test_supplier = User.objects.create(
            username="testuser", email="test@test.com", password="testUser123"
        )

        test_store = Store.objects.create(
            name="test store name", supplier=test_supplier
        )

        showroom_test = models.Showroom.objects.create(
            location=location_test,
            image=SimpleUploadedFile(
                name="test_image.jpg' %}",
                content=open(
                    f"{settings.STATICFILES_DIRS[0]}/images/test/django.png", "rb"
                ).read(),
                content_type="image/png",
            ),
            visits=10,
        )

        # store can exist in multiple showrooms

        showroom_test.store.add(test_store)
        self.assertIn(showroom_test, models.Showroom.objects.filter(store=test_store))


class RequestTest(TestCase):
    fixtures = [
        "supplier.json",
        "profile.json",
        "supplier_fixtures.json",
        "manager_fixtures.json",
    ]

    def setUp(self):
        self.client = Client()
        self.test_showroom = models.Showroom.objects.all().first()
        return super().setUp()

    def test_app_urls(self):
        response = self.client.get("")
        # home
        home_found = resolve("/")
        self.assertEqual(
            home_found.func.__name__, ManagerViews.HomeView.as_view().__name__
        )

        # showrooms
        showroow_found = resolve(reverse_lazy("manager:showrooms"))
        self.assertEqual(
            showroow_found.func.__name__,
            ManagerViews.ShowRoomListView.as_view().__name__,
        )

        # # services
        # products_found = resolve("/services/")
        # self.assertEqual(products_found.func.__name__, views.ProductListView.as_view().__name__)

        # # support
        # products_found = resolve("/support/")
        # self.assertEqual(products_found.func.__name__, views.ProductListView.as_view().__name__)

        # # about-us
        # products_found = resolve("/about-us/")
        # self.assertEqual(products_found.func.__name__, views.ProductListView.as_view().__name__)

    def test_home_page(self):
        # a request is made to that base app
        response = self.client.get("")

        # template used
        self.assertTemplateUsed(response, "manager/home.html")

        # view context
        view_context = [
            "view_name",
            "product_categories",
            "showrooms",
            "discounts",
            "catogory_product_group",
            "new_arrivals",
        ]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

    def test_showroom_view(self):
        response = self.client.get(reverse_lazy("manager:showrooms"))

        self.assertEqual(response.status_code, 200)

        # template used
        self.assertTemplateUsed(response, "manager/showroom_list.html")

        # view context
        view_context = ["view_name", "locations"]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        self.assertIn(self.test_showroom, response.context.get("object_list"))

    def test_showroom_detail_view(self):

        response = self.client.get(
            reverse_lazy("manager:showroom-detail", args=[self.test_showroom.slug])
        )

        self.assertEqual(response.status_code, 200)

        # template used
        self.assertTemplateUsed(response, "manager/showroom_detail.html")

        view_context = ["view_name", "stores", "other_showroom"]

        for context_name in view_context:
            self.assertIn(context_name, response.context)

        self.assertEqual(self.test_showroom, response.context.get("object"))

        # view_context = ["view_name", "stores", "other_store"]

        # for context_name in view_context:
        #     self.assertIn(context_name, response.context)

        # self.assertEqual(self.test_store, response.context.get('object'))
