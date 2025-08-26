from urllib import request
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from admin_api import serializers
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from supplier import models as SupplierModels
from payment import models as PaymentModels
from auth_app import models as AuthModels
from manager import models as ManagerModels
from buyer import models as BuyerModels
from coms import models as ComsModels

from admin_api import serializers
import supplier
import uuid


import pandas as pd
from datetime import datetime
from datetime import timezone


class CustomListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class LargeCustomListPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"


class StoresListView(ListAPIView):
    serializer_class = serializers.StoreSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return SupplierModels.Store.objects.filter(supplier=self.request.user)

class ContractsListView(ListAPIView):
    serializer_class = serializers.ContractsSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return PaymentModels.Contract.objects.filter(Q(buyer=self.request.user))


class SupplierContractsListView(ListAPIView):
    serializer_class = serializers.ContractsSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return PaymentModels.Contract.objects.filter(Q(supplier=self.request.user))


class ServicesListView(ListAPIView):
    serializer_class = serializers.ServiceSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return SupplierModels.Service.objects.filter(supplier=self.request.user)



#---------------------------------------- Products ----------------------------------------
class ProductsListView(ListAPIView):
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination
    queryset = SupplierModels.Product.objects.all()
    
class SupplierProductsListView(ListAPIView):
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return SupplierModels.Product.admin_list.filter(
            store__in=SupplierModels.Store.objects.filter(supplier=self.request.user)
        )

class ProductCreateApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ProductsSerializer

    def post(self, request, *args, **kwargs):
        sub_category = SupplierModels.ProductSubCategory.objects.filter(name=request.data.get("sub_category"))
        if not sub_category:
            return Response(_("Invalid Product Sub Category Selected."), status=status.HTTP_404_NOT_FOUND)

        request.data["sub_category"] = sub_category.first().id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        product = SupplierModels.Product.admin_list.filter(id = serializer.data.get("id"))
        product.first().business = AuthModels.ClientProfile.objects.filter(user=request.user).first()
        product.first().save()

        return Response(
            {
                "message": _("Product Details Created Successfully."),
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    

class ProductAppendDetailsApiView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.ProductsSerializer

    def post(self, request, slug, data_type):
        product = SupplierModels.Product.admin_list.filter(slug=slug)
        if not product:
            return Response(_("Product Not Found."), status=status.HTTP_404_NOT_FOUND)
        product = product.first()

        if data_type == "media":
            images_saved = 0
            videos_saved = 0

            images = request.FILES.getlist('images')            
            # store product images
            for image in images:
                product_image = SupplierModels.ProductImage(product=product, image=image)
                if product_image:
                    product_image.save()
                    images_saved += 1

            videos = request.FILES.getlist('videos')
            # store product videos
            for video in videos:
                product_video = SupplierModels.ProductVideo(product=product, video=video)
                if product_video:
                    product_video.save()
                    videos_saved += 1

            return Response(
                {
                    "message": _("{:d} Images, {:d} Videos Saved Successfully.".format(images_saved, videos_saved)),
                    "data": {}
                },
                status=status.HTTP_201_CREATED,
            )

        elif data_type == "store":
            store = SupplierModels.Store.objects.filter(name=request.data.get("store"))
            if not store:
                return Response(_("Selected Store Not Found."), status=status.HTTP_404_NOT_FOUND)

            # add product to store
            store.first().store_product.add(product)
            # set product stock
            if request.data.get("stock"):
                product.stock = int(request.data.get("stock"))
                product.save(update_fields=['stock'])

            return Response(
                {
                    "message": _("Product Details Updated Successfully."),
                    "data": {}
                },
                status=status.HTTP_201_CREATED
            )
        elif data_type == "labels":
            colors = 0
            tags = 0
            materials = 0

            for key in request.data.keys():
                if "tag" in key:
                    tag = SupplierModels.ProductTag(product=product, name=request.data.get(key))
                    tag.save()
                    tags += 1
                elif "color" in key:
                    color = SupplierModels.ProductColor(product=product, name=request.data.get(key))
                    color.save()
                    colors += 1
                elif "material" in key:
                    material = SupplierModels.ProductMaterial(product=product, name=request.data.get(key))
                    material.save()
                    materials += 1

            return Response(
                {
                    "message": _("{:d} Tags, {:d} Colors and {:d} Materials Attached to Product".format(tags, colors, materials)),
                    "data": {}
                },
                status=status.HTTP_201_CREATED
            )
        elif data_type == "pricing":
            pricings_saved = 0
            pricings = []
            for key in request.data.keys():
                if "currency" in key and "price" not in key:
                    price_num = key.split("-")[1]
                    prices = list(filter(lambda x: f"price-currency-{price_num}" in x, request.data.keys()))
                    pricing = {"currency" : key, "prices" : prices}
                    pricings.append(pricing)

            for pricing in pricings:
                # these are keys
                currency_key = pricing["currency"]
                min_price_key = list(filter(lambda p: "min" in p, pricing["prices"]))[0]
                max_price_key = list(filter(lambda p: "max" in p, pricing["prices"]))[0]

                price = SupplierModels.ProductPrice(
                    product=product,
                    currency = request.data[currency_key],
                    min_price = request.data[min_price_key],
                    max_price = request.data[max_price_key]
                )
                price.save()
                pricings_saved += 1
            
            return Response(
                {
                    "message": _("{:d} Pricings Attached to Product".format(pricings_saved)),
                    "data": {}
                },
                status=status.HTTP_201_CREATED
            )

class LoadingProductsListView(ListAPIView):
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return SupplierModels.Product.objects.filter(supplier=self.request.user)


#---------------------------------------- Products ----------------------------------------

# calender
class CalenderEventListView(ListAPIView):
    serializer_class = serializers.CalenderEventserializer
    pagination_class = CustomListPagination
    
    def get_queryset(self):       
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user)
        return ManagerModels.CalenderEvent.objects.filter(business=business.first())

class CalenderEventCreateView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.CalenderEventserializer

    def post(self, request, *args, **kwargs):
        del request.data["allDay"]
        business = AuthModels.ClientProfile.objects.filter(user=request.user).first()
        request.data["business"] = business.id

        request.data["start"] = datetime.fromisoformat(request.data["start"][:-1]).astimezone(timezone.utc)
        request.data["end"] = datetime.fromisoformat(request.data["end"][:-1]).astimezone(timezone.utc)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            {
                "message": _("Event Created Successfully."),
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    

class CalenderEventDetailView(generics.RetrieveAPIView):
    serializer_class = serializers.CalenderEventserializer
    pagination_class = CustomListPagination
    
    def get_queryset(self):       
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user)
        return ManagerModels.CalenderEvent.objects.filter(business=business.first())

class CalenderEventDeleteView(generics.DestroyAPIView):
    serializer_class = serializers.CalenderEventserializer
    pagination_class = CustomListPagination
    
    def get_queryset(self):       
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user)
        return ManagerModels.CalenderEvent.objects.filter(business=business.first())


# carts
class CartListView(ListAPIView):
    serializer_class = serializers.ProductVariationserializer
    
    def get_queryset(self):
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user).first()
        cart = BuyerModels.Cart.objects.filter(buyer=business)
        if not cart:
            cart = BuyerModels.Cart.objects.create(buyer=business)
        else:
            cart = cart.first()
        return SupplierModels.OrderProductVariation.objects.filter(cart=cart)
        
class CartAppeendAppendView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, product_slug):
        product = get_object_or_404(SupplierModels.Product, slug=product_slug)
        business = AuthModels.ClientProfile.objects.filter(user=request.user).first()
        cart = BuyerModels.Cart.objects.filter(buyer=business)
        if not cart:
            cart = BuyerModels.Cart.objects.create(buyer=business)
        else:
            cart = cart.first()
        
        # create product variation
        variation = SupplierModels.OrderProductVariation(
            cart = cart,
            product = product,
            price = SupplierModels.ProductPrice.objects.filter(id=request.data.get("pricing")).first(),
            color = SupplierModels.ProductColor.objects.filter(id=request.data.get("color")).first(),
            material = SupplierModels.ProductMaterial.objects.filter(id=request.data.get("material")).first(),
            quantity = int(request.data.get("quantity")),
        )
        variation.save()

        return Response(
            {
                "message": _("Product Added To Cart Successfully."),
                "data": ""
            },
            status=status.HTTP_201_CREATED,
        )
    

class CartDeleteProductView(ListAPIView):
    pass


# notifications
class NotificationListView(ListAPIView):
    serializer_class = serializers.NotificationSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return ManagerModels.Notification.objects.all()
    
class NotificationBusinessListView(ListAPIView):
    serializer_class = serializers.NotificationSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user).first()
        return ManagerModels.Notification.objects.filter(target=business)

class NotificationCategoryListView(ListAPIView):
    serializer_class = serializers.NotificationSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        return ManagerModels.Notification.objects.filter(category=self.request.GET.get("category"))

class NotificationDeleteView(DestroyAPIView):
    serializer_class = serializers.NotificationSerializer
    pagination_class = CustomListPagination
    queryset = ManagerModels.Notification.objects.all()


class NotificationUpdateView():
    pass

class ChatListView(ListAPIView):
    def get(self, request):
        interClientChats = ComsModels.InterClientChat.objects.filter(
            Q(initiator=self.request.user.business)
            | Q(participant=self.request.user.business)
        )
        interUserChats = ComsModels.InterUserChat.objects.filter(participants=self.request.user)
        groupChat = ComsModels.GroupChat.objects.filter(participants=self.request.user)

        data = {
            "business" : serializers.InterClientChatSerializer(interClientChats, many=True).data,
            "users" : serializers.InterUserChatSerializer(interUserChats, many=True).data,
            "groups" : serializers.GroupChatSerializer(groupChat, many=True).data
        }
        

        return Response(
            {
                "data": data
            },
            status=status.HTTP_200_OK
        )


class UserInfoView(RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    queryset = AuthModels.User.objects.all()
    lookup_field = "pk"

class BusinessInfoView(RetrieveAPIView):
    serializer_class = serializers.BusinessSerializer
    queryset = AuthModels.ClientProfile.objects.all()
    lookup_field = "pk"


class CreateGroupChat(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.GroupChatSerializer

    def post(self, request, *args, **kwargs):
        chat = ComsModels.GroupChat.objects.create(roomname=uuid.uuid4(), name=request.data.get("name"))
        chat.participants.add(request.user)
        return Response(
            {
                "data": chat.roomname
            },
            status=status.HTTP_201_CREATED,
        )