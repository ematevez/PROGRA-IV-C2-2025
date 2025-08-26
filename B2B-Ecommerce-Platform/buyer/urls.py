from django.urls import path

app_name = "buyer"

from buyer import views

urlpatterns = [
    path("dashboard/profile/", views.ProfileView.as_view(), name="profile"),
    path("password-reset", views.password_reset, name="password-reset"),
    path(
        "editaccountsprofile/",
        views.EditAccountsProfileView.as_view(),
        name="dashboard-editaccountsprofile",
    ),
    path("business/", views.BusinessProfileView.as_view(), name="business"),
    path(
        "editbusinessprofile/<str:slug>/",
        views.EditBusinessProfileView.as_view(),
        name="dashboard-editbusinessprofile",
    ),
    path("contracts/", views.ContractListView.as_view(), name="contracts"),
    path("request-for-quote/", views.RequestForQuoteView.as_view(), name="request-for-quote"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("calendar/", views.CalendarView.as_view(), name="calendar"),
    path("bids/", views.BidsView.as_view(), name="bids"),
    path("bids-compare/", views.BidsCompareView.as_view(), name="bids-compare"),
    path("notifications/", views.NotificationsView.as_view(), name="notifications"),
    path("bids/", views.BidsView.as_view(), name="bids"),
    path("reporting-analytics/", views.ReportingAnalyticsView.as_view(), name="reporting-analytics"),
    path(
        "dashboard/contractsdetails/<int:pk>",
        views.DashboardContractsDetailsView.as_view(),
        name="dashboard-contractsdetails",
    ),
    path("product/", views.VisitedProductsListView.as_view(), name="products"),


    #---------------------------------------- WishList ----------------------------------------
    path("dashboard/wishlist/", views.WishListListView.as_view(), name="wishlist"),
    path("dashboard/wishlist/product/<str:product_slug>/add/", views.WishListAppeendAppendView.as_view(), name="wishlist-add-product"),
    path("dashboard/wishlist/product/<str:product_slug>/delete/", views.WishListDeleteProductView.as_view(), name="wishlist-delete-product"),
    #---------------------------------------- WishList ----------------------------------------

    
    #---------------------------------------- Chart ----------------------------------------
    path("dashboard/cart/", views.CartListView.as_view(), name="cart-list"),
    path("dashboard/cart/product/<int:pk>/delete/", views.CartDeleteProductView.as_view(), name="cart-delete-product"),
    #---------------------------------------- Chart ----------------------------------------

    #---------------------------------------- Orders ----------------------------------------
    path("dashboard/orders/list/", views.OrderTrackingView.as_view(), name="order-tracking"),
    path("dashboard/orders/<str:order_id>/", views.OrderDetaliView.as_view(), name="order-detail"),
    path("dashboard/orders/create/", views.OrderCreateView.as_view(), name="order-create"),
    path("dashboard/orders/<str:order_id>/add/product/", views.OrderAddProductView.as_view(), name="order-add-product"),
    path("dashboard/orders/<str:order_id>/shipping/details/", views.OrderShippingDetailView.as_view(), name="order-shipping-details"),
    path("dashboard/orders/product/<int:pk>/", views.ProductVariationDetails.as_view(), name="product-variation-detial"),

    # old
    path("dashboard/order-history/", views.OrderHistoryView.as_view(), name="order-history"),
    path("dashboard/orders/", views.OrdersView.as_view(), name="orders"),
    #---------------------------------------- Orders ----------------------------------------

    
    #---------------------------------------- Chats ----------------------------------------
    path("messenger/", views.MessengerView.as_view(), name="messenger"),
    #---------------------------------------- Chats ----------------------------------------
]
