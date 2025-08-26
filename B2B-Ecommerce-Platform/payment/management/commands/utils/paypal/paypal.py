import os
import paypalrestsdk
from datetime import datetime, timedelta

from django.conf import settings

def mode():
    if settings.DEBUG:
        return "sandbox"
    return "live"


paypal_api = paypalrestsdk.Api({
    "mode": mode(),  # noqa
    "client_id":  os.environ.get("PAYPAL_CLIENT_ID"),
    "client_secret": os.environ.get("PAYPAL_CLIENT_SECRET")
})


def get_url_from(iterator, what):
    for link in iterator:
        if link['rel'] == what:
            return link['href']


# def plus_days(count):
#     _date = datetime.now()
#     return _date + timedelta(days=count)


# def set_paid_until(obj, from_what):

#     if from_what == SUBSCRIPTION:
#         billing_agreement_id = obj['billing_agreement_id']
#         # get subscription details
#         ret = myapi.get(f"v1/billing/subscriptions/{billing_agreement_id}")

#         try:
#             subscription = models.Subscription.objects.filter(order_key=billing_agreement_id).first()
#         except:
#             return False

#         logger.debug(f"SUBSCRIPTION {obj}")
        

#     return True