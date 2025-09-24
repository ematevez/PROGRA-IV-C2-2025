from django.urls import path
from . import views


app_name = "presence"
urlpatterns = [
    path("session-expired/", views.session_expired, name="session_expired"),
    path("online/", views.online_users, name="online-users"),
]