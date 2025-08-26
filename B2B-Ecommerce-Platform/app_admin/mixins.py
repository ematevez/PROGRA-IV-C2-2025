from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import AccessMixin


class SupportOnlyAccessMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))

        elif not (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.account_type == "SUPPORT")
        ):
            # blocked dashboard access to mobile users
            return redirect(reverse("manager:home"))

        # if request.user_agent.is_mobile and request.user_agent.is_tablet:
        #     return redirect(reverse("manager:dashboard-blocked"))

        return super().dispatch(request, *args, **kwargs)
