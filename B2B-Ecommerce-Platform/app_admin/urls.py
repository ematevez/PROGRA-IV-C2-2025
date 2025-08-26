from django.urls import path
from app_admin import views

app_name = "app_admin"

urlpatterns = [
    path("", views.AdminDashboardView.as_view(), name="home"),
    path("clients/", views.AdminClientsView.as_view(), name="clients"),
    # manager
    path("manager/", views.AdminManagersView.as_view(), name="manager"),
    path("manager/service", views.ServiceCreateView.as_view(), name="service-create"),
    path(
        "manager/showroom", views.ShowroomCreateView.as_view(), name="showroom-create"
    ),
    path(
        "manager/category", views.CategoryCreateView.as_view(), name="category-create"
    ),
    path(
        "manager/subcategory",
        views.SubCategoryCreateView.as_view(),
        name="subcategory-create",
    ),
    # support
    path("discussions/", views.AdminDiscussionsView.as_view(), name="discussions"),
    path(
        "discussions/chat/<str:roomname>",
        views.AdminChatView.as_view(),
        name="discussion",
    ),
    path("community/", views.AdminCommunityView.as_view(), name="community"),
    path(
        "community/chat/<str:slug>",
        views.AdminCommunityChatView.as_view(),
        name="community-chat",
    ),
    path(
        "community/delete/<str:slug>",
        views.AdminDiscussionDeleteView.as_view(),
        name="community-chat-delete",
    ),
    # contact
    path("contact/<str:slug>", views.ContactClient.as_view(), name="contact"),
    # profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("editprofile/", views.EditProfileView.as_view(), name="editprofile"),
    path("createsupport/", views.CreateSupportView.as_view(), name="createsupport"),
    path(
        "activate/<uidb64>/<token>/", views.VerficationView.as_view(), name="activate"
    ),

    path("promotions/", views.AdminPromotionsView.as_view(), name="promotions"),
    path("promotions/create/", views.AdminPromotionsCreateView.as_view(), name="promotions-create"),
    path("promotions/edit/<str:slug>", views.AdminPromotionsEditView.as_view(), name="promotions-edit"),
    
    path("promotions/emails/", views.AdminEmailPromotionsView.as_view(), name="email-promotions"),
    path("promotions/emails/create/", views.AdminEmailPromotionsCreateView.as_view(), name="email-promotions-create"),
    path("promotions/emails/edit/<str:slug>", views.AdminEmailPromotionsEditView.as_view(), name="email-promotions-edit"),
    path("promotions/emails/send/<str:slug>", views.AdminEmailPromotionsSendView.as_view(), name="email-promotions-send"),
]
