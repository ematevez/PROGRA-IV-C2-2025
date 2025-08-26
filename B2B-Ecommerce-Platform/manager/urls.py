from django.urls import path

# apps
from manager import views

app_name = "manager"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # showrooms
    path("showrooms/", views.ShowRoomListView.as_view(), name="showrooms"),
    path(
        "showroom/<str:slug>",
        views.ShowRoomDetailView.as_view(),
        name="showroom-detail",
    ),
    # services
    path("services/", views.ServiceListView.as_view(), name="services"),
    path("about/", views.AboutUsView.as_view(), name="about-us"),
    path("profile/", views.profile, name="profile"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("support/", views.SupportView.as_view(), name="support"),
    path("support/chatroom/", views.SupportChatroomView.as_view(), name="chatroom"),
    path(
        "support/discussion/<str:slug>/",
        views.SupportDiscussionView.as_view(),
        name="discussion",
    ),
    path(
        "support/discussions/",
        views.SupportDiscussionListView.as_view(),
        name="discussions",
    ),
    path(
        "support/create-discussion/",
        views.SupportCreateDiscussionView.as_view(),
        name="create-discussion",
    ),
    path("blocked", views.blockDasboardAccess, name="dashboard-blocked"),
    path("profile404", views.ProfileNotFound, name="profile-notfound"),
    # guides
    path("guides/memberships", views.memberships, name="guides-memberships"),
    path("guides/showrooms", views.showrooms, name="guides-showrooms"),
    path("guides/stores", views.stores, name="guides-stores"),
    path("guides/services", views.services, name="guides-services"),
    path("guides/products", views.products, name="guides-products"),
    path("guides/accounts", views.accounts, name="guides-accounts"),
]
