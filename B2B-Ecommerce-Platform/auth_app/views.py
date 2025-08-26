from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseNotFound

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from auth_app import models as AuthModels

from auth_app.forms import UserProfileFormManager

from auth_app import tasks as AuthTask
from auth_app.tokens import appTokenGenerator

from payment.management.commands.utils.braintree import braintree_config


class LoginView(View):
    template_name = "auth_app/signin.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("manager:home"))
        context_data = {"view_name": _("Sign In")}

        return render(request, self.template_name, context=context_data)

    def post(self, request):
        if not (request.POST.get("username") and request.POST.get("password")):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("auth_app:login"))

        user = authenticate(
            username=request.POST.get("username"), password=request.POST.get("password")
        )
        if not user:
            messages.add_message(
                request, messages.ERROR, _("Account not found. Try Again.")
            )
            return redirect(reverse("auth_app:login"))

        if not user.is_email_activated:
            messages.add_message(
                request, messages.ERROR, _("Please Activate your Email")
            )
            return redirect(reverse("auth_app:login"))

        login(request, user)
        if request.GET.get("next"):
            return redirect(reverse(request.GET.get("next")))
        return redirect(reverse("manager:home"))


class SignUpView(View):
    template_name = "auth_app/signup.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("manager:home"))

        if request.GET.get("Supplier"):
            account_type = "Supplier"
        elif request.GET.get("Buyer"):
            account_type = "Buyer"
        else:
            return redirect(reverse("auth_app:login"))

        context_data = {"view_name": _("Sign Up"), "account_type": account_type}

        return render(request, self.template_name, context=context_data)

    def post(self, request):
        if request.POST.get("account_type") == "Supplier":
            account_type = request.POST.get("account_type")
            UserModel = AuthModels.Supplier
        elif request.POST.get("account_type") == "Buyer":
            account_type = "Buyer"
            UserModel = AuthModels.Buyer
        else:
            return redirect(reverse("auth_app:login"))

        if not (
            request.POST.get("first_name")
            and request.POST.get("last_name")
            and request.POST.get("username")
            and request.POST.get("email")
            and request.POST.get("password")
            and request.POST.get("confirm-password")
        ):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(
                "{}?{}=1".format(reverse("auth_app:signup"), account_type.lower())
            )

        if AuthModels.User.objects.filter(username=request.POST.get("username")):
            messages.add_message(request, messages.ERROR, _("Username not available."))
            return redirect(
                "{}?{}=1".format(reverse("auth_app:signup"), account_type.lower())
            )

        if AuthModels.User.objects.filter(email=request.POST.get("email")):
            messages.add_message(request, messages.ERROR, _("Email not available."))
            return redirect(
                "{}?{}=1".format(reverse("auth_app:signup"), account_type.lower())
            )

        if request.POST.get("confirm-password") != request.POST.get("password"):
            messages.add_message(request, messages.ERROR, _("Password mismatch."))
            return redirect(
                "{}?{}=1".format(reverse("auth_app:signup"), account_type.lower())
            )

        user = UserModel.objects.create_user(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            username=request.POST.get("username"),
            email=request.POST.get("email"),
            password=request.POST.get("password"),
            account_type=account_type,
        )

        fields = ("first_name", "last_name")
        AuthTask.make_user_translations.delay(fields, user.pk)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = appTokenGenerator.make_token(user)
        domain = get_current_site(request).domain
        link = reverse("auth_app:activate", kwargs={"uidb64": uidb64, "token": token})

        activate_url = f"{domain}{link}"

        subject = _("Activate Foroden Activation")
        description = "{}\n{}\n{}".format(_("Follow this link to activate you foroden account."), _("Your activation link is"), activate_url)

        AuthTask.send_account_activation_email_task.delay(user.username, user.email, subject, description)

        messages.add_message(
            request,
            messages.SUCCESS,
            _(
                "Account Created Successfully. Please check your email for a verfication link."
            ),
        )
        return redirect(reverse("auth_app:login"))


class VerficationView(View):
    def get(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = AuthModels.User.objects.filter(pk=uid).first()

        if user and appTokenGenerator.check_token(user, token):
            user.is_email_activated = True
            user.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            # to dashboard
            return redirect(reverse("auth_app:business"))
        else:
            return HttpResponseNotFound(_("Bad Request"))


def LogoutView(request):
    logout(request)
    return redirect(reverse("auth_app:login"))


class BusinessProfileView(View):
    template_name = "auth_app/business_infor.html"

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))

        if AuthModels.ClientProfile.objects.filter(user=request.user):
            return redirect(reverse("manager:home"))

        context_data = {"view_name": _("Business Profile")}

        return render(request, self.template_name, context=context_data)

    def post(self, request):
        if not (
            request.POST.get("business_name")
            and request.POST.get("business_description")
            and request.POST.get("country")
            and request.POST.get("city")
        ):
            messages.add_message(
                request, messages.ERROR, _("Please Fill all reqiured fields.")
            )
            return redirect(reverse("auth_app:business"))

        try:
            profile = AuthModels.ClientProfile.objects.create(
                user=request.user,
                business_name=request.POST.get("business_name"),
                business_description=request.POST.get("business_description"),
                country=request.POST.get("country"),
                city=request.POST.get("city"),
                country_code=request.POST.get("country_code"),
                mobile_user=request.POST.get("mobile_user"),
                vat_number=request.POST.get("vat_number", None),
                legal_etity_identifier=request.POST.get("legal_etity_identifier", None),
                website=request.POST.get("website", None),
            )

            fields = (
                "business_name",
                "business_description",
                "country",
                "country_code",
                "city",
                "mobile_user",
            )
            AuthTask.make_business_translations.delay(fields, profile.pk)

            # create braintree customer
            result = braintree_config.get_braintree_gateway().customer.create(
                {
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "company": profile.business_name,
                    "email": profile.user.email,
                    "phone": profile.mobile_user,
                }
            )
            if result.is_success:
                profile.customer_id = result.customer.id
                profile.save()

            if profile.user.account_type == "SUPPLIER":
                return redirect(reverse("payment:memberships"))

            return redirect(reverse("supplier:dashboard"))
        except Exception as e:
            print("Error:", e)
            messages.add_message(
                request, messages.ERROR, _("An Error Occurred. Try Again.")
            )
            return redirect(reverse("auth_app:business"))
