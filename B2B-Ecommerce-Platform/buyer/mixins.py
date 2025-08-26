from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import AccessMixin

from auth_app import models as AuthModels

class BuyerOnlyAccessMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))
        if not (request.user.is_authenticated and request.user.account_type == "BUYER"):
            return redirect(reverse("manager:home"))

        # if request.user_agent.is_mobile and request.user_agent.is_tablet:
        #     return redirect(reverse("manager:dashboard-blocked"))
        
        if not AuthModels.ClientProfile.objects.filter(user=request.user):
            return redirect(reverse("manager:profile-notfound"))

        return super().dispatch(request, *args, **kwargs)
