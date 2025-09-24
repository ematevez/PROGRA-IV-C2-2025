from django.urls import path
from . import views

app_name = "simple_chat"
urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("api/messages/", views.messages_api, name="messages-api"),
    path("api/post/", views.post_message_api, name="post-api"),
]
