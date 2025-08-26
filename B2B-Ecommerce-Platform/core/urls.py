from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext as _

from manager import views
from payment.views import InitSubscriptionView

from django.core.signals import request_finished
from django.dispatch import receiver


# @receiver(request_finished)
# def my_callback(sender, **kwargs):
#     print("Request finished!")


# @receiver(request_finished)
# def requestTracker(request, **kwargs):
#     print(kwargs)
#     # if request.user_agent.is_mobile:
#     #     user_device = "mobile"
#     # elif request.user_agent.is_tablet:
#     #     user_device = "tablet"
#     # elif request.user_agent.is_bot:
#     #     user_device = "bot"
#     # else:
#     #     user_device = "pc"


#     print("*"*50)
#     print("Request finished!")
#     print("*"*50)
#     pass


# @receiver(got_request_exception)
# def get_exception_response(request, resolver, status_code, exception, sender=None):
# try:
#     callback, param_dict = resolver.resolve_error_handler(status_code)
#     response = callback(request, **dict(param_dict, exception=exception))
# except Exception:
#     signals.got_request_exception.send(sender=sender, request=request)
#     response = handle_uncaught_exception(request, resolver, sys.exc_info())

# return response
# pass


urlpatterns = i18n_patterns(
    path("", include("manager.urls", namespace="manager")),
    path(_("suppliers/"), include("supplier.urls", namespace="supplier")),
    path(_("buyer/"), include("buyer.urls", namespace="buyer")),
    path(_("auth/"), include("auth_app.urls", namespace="auth")),
    path(_("payments/"), include("payment.urls", namespace="payments")),
    path(_("support/admin/"), include("app_admin.urls", namespace="app_admin")),
    path(_("api/"), include("api.urls", namespace="api")),
    path(_("admin-api/"), include("admin_api.urls", namespace="admin-api")),
    path(_("communications/"), include("coms.urls", namespace="coms")),
    path(_("admin/"), admin.site.urls),
)
urlpatterns += [
    path("accounts/inactive/", InitSubscriptionView.as_view()),
    path("accounts/profile/", views.HomeView.as_view()),
    path("accounts/", include("allauth.urls")),
]

if "rosetta" in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r"^rosetta/", include("rosetta.urls"))]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
