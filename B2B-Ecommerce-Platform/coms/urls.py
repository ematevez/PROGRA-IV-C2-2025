from django.urls import path
from coms import views as ComsViews

app_name = "coms"


urlpatterns = [
    path("interclient/<str:business_slug>/", ComsViews.InterClientChatInitView.as_view(), name="interclient-chat-init"),
    path("groups/<str:roomname>/", ComsViews.GroupChatAppendView.as_view(), name="group-chat-append"),
]