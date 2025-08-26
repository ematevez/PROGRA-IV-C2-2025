from django.urls import path

# apps
from supplier import views

app_name = "supplier"

urlpatterns = [
    # supplier
    path(
        "supplier/<str:slug>",
        views.SupplierDetailView.as_view(),
        name="supplier-detail",
    ),
    path(
        "supplier/<str:slug>/contact/",
        views.SupplierContactView.as_view(),
        name="supplier-contact",
    ),
    path(
        "supplier/contract/<str:slug>/",
        views.SupplierContractView.as_view(),
        name="supplier-contract",
    ),
    # products
    path("products/", views.ProductListView.as_view(), name="products"),
    path(
        "products/<str:slug>", views.ProductDetailView.as_view(), name="product-detail"
    ),
    path("new-arivals/", views.NewArrivalView.as_view(), name="new-arivals"),
    path("superdeals/", views.SuperDealsView.as_view(), name="superdeals"),
    # categories
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path(
        "category/<str:slug>",
        views.CategoryDetailView.as_view(),
        name="category-detail",
    ),
    # subcategory
    path(
        "category/<str:category_slug>/subcategory/<str:sub_category_slug>",
        views.SubCategoryDetailView.as_view(),
        name="subcategory-detail",
    ),
    # store
    path(
        "store/<str:slug>",
        views.StoreDetailView.as_view(),
        name="store-detail",
    ),
    path(
        "stores",
        views.StoreListView.as_view(),
        name="store-list",
    ),
    # path("stores/", views.CategoryListView.as_view(), name="store-list"),
    # path(
    #     "category/<str:slug>",
    #     views.CategoryDetailView.as_view(),
    #     name="category-detail",
    # ),
    path(
        "search",
        views.SearchView.as_view(),
        name="search",
    ),
    # dashboard
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("business/profile/", views.BusinessProfileView.as_view(), name="business_profile"),
    path("password-reset", views.password_reset, name="password-reset"),
    path(
        "editaccountsprofile/",
        views.EditAccountsProfileView.as_view(),
        name="dashboard-editaccountsprofile",
    ),
    path(
        "editbusinessprofile/<str:slug>/",
        views.EditBusinessProfileView.as_view(),
        name="dashboard-editbusinessprofile",
    ),
    path(
        "dashboard/products",
        views.DashboardProductsView.as_view(),
        name="dashboard-products",
    ),
    path(
        "dashboard/productscreate",
        views.DashboardProductsCreateView.as_view(),
        name="dashboard-productscreate",
    ),
    path(
        "dashboard/product/<str:slug>/edit/",
        views.DashboardProductEditView.as_view(),
        name="dashboard-productedit",
    ),
    path(
        "dashboard/product/customize/<str:slug>/",
        views.DashboardProductCustomizationView.as_view(),
        name="dashboard-productscustomize",
    ),
    path(
        "dashboard/bulkupload",
        views.DashboardBulkUploadView.as_view(),
        name="dashboard-bulkupload",
    ),
    path(
        "dashboard/product/<str:slug>/delete/",
        views.DashboardProductDeleteView.as_view(),
        name="dashboard-productdelete",
    ),
    path("dashboard/product/<str:product_slug>/store/<str:slug>/delete/", views.DashboardProductStoreDeleteView.as_view(), name="dashboard-storedelete"),
    path("dashboard/product/<str:product_slug>/category/<str:slug>/delete/", views.DashboardProductCategoryDeleteView.as_view(), name="dashboard-categorydelete"),
    path("dashboard/product/<str:product_slug>/sub_category/<str:slug>/delete/", views.DashboardProductSubCategoryDeleteView.as_view(), name="dashboard-sub_categorydelete"),
    path("dashboard/product/<str:product_slug>/pricing/<int:pk>/delete/", views.DashboardProductPricingDeleteView.as_view(), name="dashboard-pricingdelete"),
    path("dashboard/product/<str:product_slug>/tag/<int:pk>/delete/", views.DashboardProductTagDeleteView.as_view(), name="dashboard-tagdelete"),
    path("dashboard/product/<str:product_slug>/color/<int:pk>/delete/", views.DashboardProductColorDeleteView.as_view(), name="dashboard-colordelete"),
    path("dashboard/product/<str:product_slug>/material/<int:pk>/delete/", views.DashboardProductMaterialDeleteView.as_view(), name="dashboard-materialdelete"),
    path("dashboard/product/<str:product_slug>/image/<str:slug>/delete/", views.DashboardProductImageDeleteView.as_view(), name="dashboard-imagedelete"),
    path("dashboard/product/<str:product_slug>/video/<str:slug>/delete/", views.DashboardProductVideoDeleteView.as_view(), name="dashboard-videodelete"),


    path(
        "dashboard/stores/",
        views.DashboardStoresView.as_view(),
        name="dashboard-stores",
    ),
    path(
        "dashboard/stores/<str:slug>/assign-showroom/",
        views.assign_showroom,
        name="dashboard-assign-showroom",
    ),
    path(
        "dashboard/stores/<str:slug>/add-product/",
        views.add_product,
        name="dashboard-add-product",
    ),
    path(
        "dashboard/storescreate",
        views.DashboardStoresCreateView.as_view(),
        name="dashboard-storescreate",
    ),
    path(
        "dashboard/contracts",
        views.DashboardContractsView.as_view(),
        name="dashboard-contracts",
    ),
    path(
        "dashboard/contractsdetails/<int:pk>",
        views.DashboardContractsDetailsView.as_view(),
        name="dashboard-contractsdetails",
    ),
    path(
        "dashboard/contract/reject/<int:pk>",
        views.DashboardContractRejectDetailsView.as_view(),
        name="dashboard-contract-reject",
    ),
    path(
        "dashboard/contract/accept/<int:pk>",
        views.DashboardContractAcceptDetailsView.as_view(),
        name="dashboard-contract-accept",
    ),
    path(
        "dashboard/messenger",
        views.DashboardMessengerView.as_view(),
        name="dashboard-messenger",
    ),
    path(
        "dashboard/notification",
        views.DashboardNotificationView.as_view(),
        name="dashboard-notification",
    ),
    path(
        "dashboard/calendar",
        views.DashboardCalendarView.as_view(),
        name="dashboard-calendar",
    ),
    path(
        "dashboard/services",
        views.DashboardServicesView.as_view(),
        name="dashboard-services",
    ),
    path(
        "dashboard/servicescreate",
        views.DashboardServicesCreateView.as_view(),
        name="dashboard-servicescreate",
    ),

    path(
        "dashboard/advertise",
        views.DashboardAdvertiseView.as_view(),
        name="dashboard-advertise",
    ),
    path(
        "dashboard/advertise/payment/<str:slug>",
        views.DashboardAdvertisePaymentView.as_view(),
        name="dashboard-advertise-payment",
    ),
    path(
        "dashboard/payments",
        views.DashboardPaymentsView.as_view(),
        name="dashboard-payments",
    ),
    path(
        "dashboard/payments/advert",
        views.DashboardAdvertsPaymentsView.as_view(),
        name="dashboard-advert-payments",
    ),

    # orders
    path(
        "dashboard/orders/",
        views.DashboardOrderList.as_view(),
        name="dashboard-order-list",
    ),
    path(
        "dashboard/orders/<str:order_id>",
        views.DashboardOrderDetail.as_view(),
        name="dashboard-order-details",
    ),
    path('dashboard/order-excel/<str:order_id>', views.download_excel, name='order_excel'),

]
