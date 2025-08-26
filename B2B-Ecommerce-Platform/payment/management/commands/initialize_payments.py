import os
import json
import logging

from django.core.management.base import BaseCommand

from payment import models as PaymentModels

from payment.management.commands.utils.paypal import paypal as paypal_config
from payment.management.commands.utils.braintree import braintree_config

logger = logging.getLogger(__name__)

PRODUCT = "product"
PLAN = "plan"
FEATURES = "features"
ALL = "all"


PLAN_CONF_PATH = os.path.join("payment/management/commands/utils", "plans.json")
PRODUCT_CONF_PATH = os.path.join("payment/management/commands/utils/paypal", "product.json")

class Command(BaseCommand):

    help = """
        Manages Payment Features, Plans and Products
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--create",
            "-c",
            choices=[FEATURES, PRODUCT, PLAN, ALL],
            help="Creates features, product or plan"
        )
        parser.add_argument(
            "--list",
            "-l",
            choices=[FEATURES, PRODUCT, PLAN],
            help="List features, product or plan"
        )

    def create_features(self):
        with open(PLAN_CONF_PATH, "r") as f:
            features = json.load(f)
            for _feature in features:
                feature = PaymentModels.Feature(
                    custom_id = _feature['id'],
                    name = _feature['name'],
                    price = _feature['cost'],
                    description = _feature['description'],
                    billing_frequency = _feature['interval_count'],
                    currency_iso_code = _feature['currency'],
                    interval_unit = _feature['interval_unit'],
                    status = _feature['status'], 
                )
                feature.save()
                if feature:
                    print(f"Feature: {feature.name} created.")

    def create_product(self):
        with open(PRODUCT_CONF_PATH, "r") as f:
            product = json.load(f)
            ret = paypal_config.paypal_api.post("v1/catalogs/products", product)
            
            if "error" not in ret.keys():
                product = PaymentModels.PaypalProduct(
                    custom_id=product['id'],
                    name=product['name'],
                    ProductType=product['type'],
                    description=product['description']
                )
                product.save()
                print(f"Product: {product.name} created.")
            else:
                print("Product not created.")
                
    def create_plan(self):

        product = PaymentModels.PaypalProduct.objects.all().first()
        features = PaymentModels.Feature.objects.all()
        if features:
            paypal_count = 0
            braintree_count = 0

            for feature in features:
                # create paypal plan
                paypal_json = feature.to_paypal_json(product)
                paypal_response = paypal_config.paypal_api.post("v1/billing/plans", paypal_json)
                if "error" not in paypal_response.keys():
                    paypal_count += 1
                    feature.paypal_id = paypal_response.get("id")
                    feature.save()
                    print(f"Paypal plan {feature.name} created")
                else:
                    print(paypal_response.get("error"))
                
            
            for feature in features:
                # create braintree plan
                braintree_json = feature.to_braintree_json()
                braintree_response = braintree_config.get_braintree_gateway().plan.create(braintree_json)
                if braintree_response.is_success:
                    braintree_count += 1
                    print(f"Braintree plan {feature.name} created")
                else:
                    print(braintree_response)

            print(f"Created {paypal_count} paypal plans")
            print(f"Created {braintree_count} braintree plans")

    def create_all(self):
        self.create_features()
        self.create_product()
        self.create_plan()

    def list_product(self):
        ret = paypal_config.paypal_api.get("v1/catalogs/products")
        print(ret)
        logger.debug(ret)

    def list_plan(self):
        ret = paypal_config.paypal_api.get("v1/billing/plans")
        print(ret)
        logger.debug(ret)

    def create(self, what):
        if what == FEATURES:
            self.create_features()
        elif what == PRODUCT:
            self.create_product()
        elif what == ALL:
            self.create_all()
        else:
            self.create_plan()

    def list(self, what):
        if what == PRODUCT:
            self.list_product()
        else:
            self.list_plan()

    def handle(self, *args, **options):
        create_what = options.get("create")
        list_what = options.get("list")
        print(create_what)

        if create_what:
            logger.debug(f"Create a {create_what}")
            self.create(create_what)
        elif list_what:
            logger.debug(f"List {list_what}")
            self.list(list_what)
