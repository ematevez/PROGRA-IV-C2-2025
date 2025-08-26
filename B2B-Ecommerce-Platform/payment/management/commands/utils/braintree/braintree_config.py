import os
import braintree
from django.conf import settings

def get_braintree_gateway():
    if settings.BRAINTREE_PRODUCTION:
        braintree_env = braintree.Environment.Production
    else:
        braintree_env = braintree.Environment.Sandbox

    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            environment=braintree.Environment.Sandbox,
            merchant_id='zq9jqbg246n5zjt6',
            public_key='4spv6wdb3xqwbvv4',
            private_key='4fa06482b576443eaaba4021d89cb9c0'
        )
    )

    return gateway