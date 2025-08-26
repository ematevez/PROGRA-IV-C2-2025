import logging

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


from django.apps import apps

from supplier import models as SupplierModels
from auth_app import models as AuthModels
from manager import models as ManagerModels
from payment import models as PaymentModels

from manager import tasks as ManagerTasks


apps = [
    {
        "app_name":  "supplier",
        "models" : [
            {"model": SupplierModels.ProductCategory, "fields" : ("name",)},
            {"model": SupplierModels.ProductSubCategory, "fields" : ("name",)},
            {"model": SupplierModels.Store, "fields" : ("name",)},
            {"model": SupplierModels.Product, "fields" : ("name", "description", "price", "currency")},
            {"model": SupplierModels.ProductTag, "fields" : ("name",)},
            {"model": SupplierModels.Service, "fields" : ("name", "description", "price", "currency")},
            {"model": SupplierModels.ServiceTag, "fields" : ("name",)},
        ]
    },
    {
        "app_name":  "manager",
        "models" : [
            {"model": ManagerModels.Service, "fields" : ("name", "description")},
            {"model": ManagerModels.Showroom, "fields" : ("name",)},
            {"model": ManagerModels.Discussion, "fields" : ("subject", "description")},
            {"model": ManagerModels.DiscussionReply, "fields" : ("description",)},
            {"model": ManagerModels.Promotion, "fields" : ("name", "description")},
            {"model": ManagerModels.EmailPromotion, "fields" : ("subject", "description")},
            {"model": ManagerModels.AdvertisingLocation, "fields" : ("name",)},
        ]
    },
    {
        "app_name":  "payment",
        "models" : [
            {"model": PaymentModels.MembershipGroup, "fields" : ("name", "description")},
            {"model": PaymentModels.MembershipPlan, "fields" : ("name", "description")},
            {"model": PaymentModels.Feature, "fields" : ("name", "price", "currency_iso_code")},
        ]
    },
    {
        "app_name":  "auth_app",
        "models" : [
            {"model": AuthModels.ClientProfile, "fields" : (
                "business_name",
                "business_description",
                "country",
                "country_code",
                "city",
                "mobile_user",
            )},
        ]
    },
]


class Command(BaseCommand):

    help = """
        Translates the db
    """

    def handle(self, *args, **options):
        
        for app in apps:
            for app_modal in app.get('models'):
                print(f"Translating {app_modal.get('model').__name__}")
                if app_modal.get("model").__name__ in ["Discussion", "Product", "Store"]:
                    for instance in app_modal.get("model").admin_list.all():
                        ManagerTasks.make_translations(app_modal.get("fields"), instance, app_modal.get("model"))
                        print(f"{instance} Done")
                else:
                    for instance in app_modal.get("model").objects.all():
                        ManagerTasks.make_translations(app_modal.get("fields"), instance, app_modal.get("model"))
                        print(f"{instance} Done")
                print("\n")