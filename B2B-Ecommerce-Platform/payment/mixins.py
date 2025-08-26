from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import AccessMixin


class AuthedOnlyAccessMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))
        # if not (request.user.is_authenticated and request.user.account_type == "SUPPLIER"):
        #     return redirect(reverse("manager:home"))
        return super().dispatch(request, *args, **kwargs)
