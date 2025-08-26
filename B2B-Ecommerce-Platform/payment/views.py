from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages

import json, os
from django.utils import timezone

from supplier import models as SupplierModels
from auth_app import models as AuthModels
from manager import models as ManagerModels
from payment import models as PaymentModels
from payment.mixins import AuthedOnlyAccessMixin
from manager import tasks as ManagerTasks

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa

from paypalrestsdk.notifications import WebhookEvent

# payments
import braintree
from django.conf import settings

from django.utils.decorators import method_decorator

from payment.management.commands.utils.braintree import braintree_config
from payment.management.commands.utils.paypal import paypal as paypal_config

import logging

logger = logging.getLogger(__name__)


braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=os.environ.get("BRAINTREE_MERCHANT_ID"),
    public_key=os.environ.get("BRAINTREE_PUBLIC_KEY"),
    private_key=os.environ.get("BRAINTREE_PRIVATE_KEY")
)

def deactivate_feature_subscription(membership):
    if membership.membership_type == "PAYPAL":
        subscription = PaymentModels.PaypalSubscription.objects.filter(membership=membership).first()

        ret = paypal_config.paypal_api.post(f"v1/billing/subscriptions/{subscription.order_key}/suspend")
        # logger.error('PayPal Deactivation Error: %s', ret)
        if ret.get("error"):
            ret = paypal_config.paypal_api.post(f"v1/billing/subscriptions/{subscription.order_key}/cancel")
            # logger.error('PayPal Deactivation Result: %s', ret)

        membership.status = False
        membership.save()
    else:
        subscription = PaymentModels.BraintreeSubscription.objects.filter(membership=membership).first()

        result = braintree.Subscription.cancel(subscription.subscription_id)
        if result.is_success and result.subscription.status == "Canceled":
            membership.status = False
            membership.save()

def deactivate(feature, request):
    membership_group = feature.features_list.first().group.group_type
    active_memberships = PaymentModels.Membership.active.filter(client = request.user)
    for membership in active_memberships:
        if membership.feature.features_list.first().group.group_type == membership_group:
            deactivate_feature_subscription(membership)

@method_decorator(csrf_exempt, name='dispatch')
class webhooksView(View):
    def post(self, request, *args, **kwargs):
        
        # notification = braintree_config.get_braintree_gateway().webhook_notification.parse(request.body.decode('utf-8'))

        if webhook_notification.kind == braintree.WebhookNotification.Kind.SubscriptionChargedSuccessfully:
            # Handle subscription charged successfully event
            pass
        elif webhook_notification.kind == braintree.WebhookNotification.Kind.SubscriptionCanceled:
            # Handle subscription canceled event
            pass

class InitSubscriptionView(View):
    template_name = "payments/initsubscription.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))
            
        user_profile = AuthModels.ClientProfile.objects.filter(
            user=request.user
        ).first()

        context_data = {
            "view_name": _("Business Profile"),
            "membership_groups": [
                {
                    "group" : group,
                    "plans" : [
                        {
                            "plan": plan,
                            "features": plan.features.all()
                        } for plan in group.membershipplan_set.all()
                    ]
                } for group in PaymentModels.MembershipGroup.objects.all()
            ]
        }
        
        
        if user_profile and user_profile.user.account_type == "SUPPLIER":
            if not user_profile.customer_id:
                # create braintree customer
                result = braintree.Customer.create(
                    {
                        "first_name": user_profile.user.first_name,
                        "last_name": user_profile.user.last_name,
                        "company": user_profile.business_name,
                        "email": user_profile.user.email,
                        "phone": user_profile.mobile_user,
                    }
                )
                if result.is_success:
                    user_profile.customer_id = result.customer.id
                    user_profile.save()

            try:
                braintree_client_token = braintree.ClientToken.generate(
                    {"customer_id": user_profile.customer_id}
                )
            except:
                braintree_client_token = braintree.ClientToken.generate({})

            context_data["braintree_client_token"] = braintree_client_token


        return render(request, self.template_name, context=context_data)

    def post(self, request):
        nonce_from_the_client = request.POST["paymentMethodNonce"]
        method = request.POST["method"]
        plan_id = request.POST["plan_id"]

        
        user_profile = AuthModels.ClientProfile.objects.filter(
            user=request.user
        ).first()

        
        feature = PaymentModels.Feature.objects.filter(custom_id=plan_id).first()

        # has a running subscription
        deactivate(feature, request)

        # handle cards
        result = braintree.Subscription.create(
            {"payment_method_nonce": nonce_from_the_client, "plan_id": plan_id}
        )

        if result.is_success:
            membership = PaymentModels.Membership.objects.create(
                membership_type = "BRAINTREE CARD",
                client = user_profile.user,
                feature = feature,
                previous_feature = None,
                upgrading_to = feature,
                start_date = result.subscription.billing_period_end_date,
                expiry_date = result.subscription.billing_period_start_date,
                status = True,
                payment_completed = True,
            )


            subscription = PaymentModels.BraintreeSubscription.objects.create(
                membership = membership,
                subscription_id = result.subscription.id,
                payment_method = method,
                current_billing_cycle = result.subscription.current_billing_cycle,
                days_past_due = result.subscription.days_past_due,
                next_billing_date = result.subscription.next_billing_date,
                payment_method_token = result.subscription.payment_method_token,
            )

            if method == "CARD":
                PaymentModels.CardPayment.objects.create(
                    subscription = subscription,
                    card_token = result.subscription.transactions[0].credit_card_details.token,
                    card_last_4 = result.subscription.transactions[0].credit_card_details.last_4,
                    card_type = result.subscription.transactions[0].credit_card_details.card_type,
                    card_expiration_month = result.subscription.transactions[0].credit_card_details.expiration_month,
                    card_expiration_year = result.subscription.transactions[0].credit_card_details.expiration_year,
                    card_customer_location = result.subscription.transactions[0].credit_card_details.customer_location,
                    card_issuing_bank = result.subscription.transactions[0].credit_card_details.issuing_bank,
                )

            # send mail
            return HttpResponse("SUCCESSFUL", status=200)

        print(result)
        return HttpResponse(_("Already subcribed to this plan"), status=401)

def deactivateSubcription(request):
    if request.method == "POST":
        plan_id = request.POST.get("plan_id")
        feature = PaymentModels.Feature.objects.filter(custom_id=plan_id).first()
        membership = PaymentModels.Membership.active.filter(client = request.user, feature=feature).first()
        deactivate_feature_subscription(membership)
        return redirect(reverse("supplier:profile"))
    else:
        return redirect(reverse("supplier:profile"))



class CreatePaypalSubscription(View):

    def post(self, request, *args, **kwargs):
        method = request.POST["method"]
        plan_id = request.POST["plan_id"]

        user_profile = AuthModels.ClientProfile.objects.filter(
            user=request.user
        ).first()

        feature = PaymentModels.Feature.objects.filter(custom_id=plan_id).first()

        # has a running subscription
        deactivate(feature, request)

        try:
            data = {
                "plan_id": feature.paypal_id
            }

            ret = paypal_config.paypal_api.post("v1/billing/subscriptions", data)
            if ret.get("error"):
                return HttpResponse(_("Unable to update your subscription."), status=401)

            if ret.get('status') == 'APPROVAL_PENDING':

                membership = PaymentModels.Membership.objects.create(
                    membership_type = "PAYPAL",
                    client = user_profile.user,
                    feature = feature,
                    previous_feature = None,
                    upgrading_to = feature,
                    status = False,
                    payment_completed = False,
                )

                subcription = PaymentModels.PaypalSubscription.objects.create(
                    membership = membership,
                    order_key = ret['id']
                )

                redirect_url = paypal_config.get_url_from(ret['links'], 'approve')

                return JsonResponse({"status" : "SUCCESSFUL", "url":  redirect_url}, status=200)
        except Exception as e:
            print("Err:", e)
            return HttpResponse(status=401)



@require_POST
@csrf_exempt
def paypal_webhooks(request):
    transmission_id = request.headers['Paypal-Transmission-Id']
    timestamp = request.headers['Paypal-Transmission-Time']
    webhook_id = os.environ.get("PAYPAL_WEBHOOK_ID")
    event_body = request.body.decode('utf-8')
    cert_url = request.headers['Paypal-Cert-Url']
    auth_algo = request.headers['Paypal-Auth-Algo']
    actual_signature = request.headers['Paypal-Transmission-Sig']

    response = WebhookEvent.verify(
        transmission_id,
        timestamp,
        webhook_id,
        event_body,
        cert_url,
        actual_signature,
        auth_algo
    )
    if response:
        obj = json.loads(request.body)
        event_type = obj.get('event_type')
        resource = obj.get('resource')

    try:

        if resource.get("status", None) == 'APPROVAL_PENDING':
            billing_agreement_id = resource['id']
            subscription = PaymentModels.PaypalSubscription.objects.filter(order_key=billing_agreement_id).first()
            user = AuthModels.Supplier.objects.filter(id=subscription.membership.client.id).first()

            subject = _("Foroden Subscription")
            message = _("Your payment as been initialized. Please wait for confirmation email.")

            ManagerTasks.send_mail.delay(
                subject = subject,
                content = f'Hello, {user.profile().business_name}, \n{message}',
                _to = [f"{user.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

        elif resource.get("status", None) == 'ACTIVE':
            
            billing_agreement_id = resource['id']
            subscription = PaymentModels.PaypalSubscription.objects.filter(order_key=billing_agreement_id).first()
            user = AuthModels.Supplier.objects.filter(id=subscription.membership.client.id).first()

            subject = _("Foroden Subscription")
            message = _("Your payment was successfull.")

            ManagerTasks.send_mail.delay(
                subject = subject,
                content = f'Hello, {user.profile().business_name}, \n{message}',
                _to = [f"{user.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

            subscription.membership.status = True
            subscription.membership.payment_completed = True
            subscription.membership.save()

        elif resource.get("status", None) == "SUSPENDED":
            billing_agreement_id = resource['id']
            subscription = PaymentModels.PaypalSubscription.objects.filter(order_key=billing_agreement_id).first()
            ret = mode.myapi.post(f"v1/billing/subscriptions/{subscription.order_key}/cancel")
            
            if not ret.get("error"):
                user = AuthModels.Supplier.objects.filter(id=subscription.membership.client.id).first() 
                subject = _("Foroden Subscription")
                message = _("Your subscription was deactivated successfully.")

                ManagerTasks.send_mail.delay(
                    subject = subject,
                    content = f'Hello, {user.profile().business_name}, \n{message}',
                    _to = [f"{user.email}"],
                    _reply_to = [f"{settings.SUPPORT_EMAIL}"]
                )

                subscription.membership.status = False
                subscription.membership.payment_completed = True
                subscription.membership.save()

        elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
            billing_agreement_id = resource['id']
            subscription = PaymentModels.PaypalSubscription.objects.filter(order_key=billing_agreement_id).first()
            
            if not ret.get("error"):
                user = AuthModels.Supplier.objects.filter(id=subscription.membership.client.id).first()
                subject = _("Foroden Subscription")
                message = _("Your subscription was deactivated successfully.")

                ManagerTasks.send_mail.delay(
                    subject = subject,
                    content = f'Hello, {user.profile().business_name}, \n{message}',
                    _to = [f"{user.email}"],
                    _reply_to = [f"{settings.SUPPORT_EMAIL}"]
                )

                subscription.membership.status = False
                subscription.membership.payment_completed = True
                subscription.membership.save()

        return HttpResponse(status=200)
    except:
        pass


class ContractPaymentView(View):
    template_name = "payments/contract_payment.html"

    def get(self, request, pk):
        contract = PaymentModels.Contract.objects.filter(pk=pk).first()

        context_data = dict()
        context_data["view_name"] = "Contract Payment"
        context_data["contract"] = contract

        return render(request, self.template_name, context=context_data)
    
    def post(self, request, pk):

        contract = PaymentModels.Contract.objects.filter(pk=pk).first()
        context_data = dict()
        context_data["view_name"] = "Contract Payment"
        context_data["contract"] = contract

        # return render(request, "payments/contract_receipt.html", context=context_data)
        pdf = render_to_pdf("payments/contract_receipt.html", context_data)
        return HttpResponse(pdf, content_type="application/pdf")

def contract_receipt(request, pk):
    if request.method == "POST":

        contract = PaymentModels.Contract.objects.filter(pk=pk).first()
        context_data = dict()
        context_data["view_name"] = "Contract Payment"
        context_data["contract"] = contract

        # return render(request, "payments/contract_receipt.html", context=context_data)
        pdf = render_to_pdf("payments/contract_receipt.html", context_data)
        return HttpResponse(pdf, content_type="application/pdf")

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None