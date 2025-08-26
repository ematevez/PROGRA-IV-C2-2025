from django.urls import path

app_name = "auth_app"

from auth_app import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    # path('signup-buyer', views.SignUpView.as_view(), name='signup-buyer'),
    path(
        "activate/<uidb64>/<token>/", views.VerficationView.as_view(), name="activate"
    ),
    path("signup/business/", views.BusinessProfileView.as_view(), name="business"),
    path("logout", views.LogoutView, name="logout"),
]
