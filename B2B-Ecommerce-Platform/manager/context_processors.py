from supplier import models as SupplierModels
from auth_app import models as AuthModels
from manager import models as ManagerModels
from admin_api.serializers import CalenderEventserializer

def categories_showroows(request):
    context = dict()
    context[
        "categories_header"
    ] = SupplierModels.ProductCategory.objects.all().order_by("-id")[:7]
    context["showroows_headers"] = ManagerModels.Showroom.objects.all().order_by("-id")[
        :6
    ]

    return context

# def calender_events(request):
#     context = dict()
#     if request.user.id:
#         business = AuthModels.ClientProfile.objects.filter(user=request.user)
#         if business:
#             business = business.first()
#             saved_events = ManagerModels.CalenderEvent.objects.filter(business=business)
#             if saved_events:
#                 events = CalenderEventserializer(saved_events, many=True).data
#                 context["business_events"] = events

#     return context
