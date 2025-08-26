from rest_framework import serializers
from datetime import datetime
from auth_app import models as AuthModels
from supplier import models as SupplierModels
from buyer import models as BuyerModels
from manager import models as ManagerModels
from payment import models as PaymentModels
from coms import models as ComsModels

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthModels.User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "account_type",
            "is_active",
            "image",
            "date_joined",
        )

class BusinessSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=AuthModels.User.objects.all())
    class Meta:
        model = AuthModels.ClientProfile
        fields = "__all__"

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModels.Membership
        fields = "__all__"


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductCategory
        fields = "__all__"


class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductSubCategory
        fields = "__all__"
        depth = 1


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.Store
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["products"] = (
            SupplierModels.Store.admin_list.filter(id=instance.id)
            .first()
            .store_product.all()
            .count()
        )
        return representation


class SuppliersSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AuthModels.ClientProfile
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["membership"] = PaymentModels.Membership.objects.filter(
            client=instance.user
        ).first().feature.name
        representation["stores"] = SupplierModels.Store.admin_list.filter(
            supplier=instance.user
        ).count()
        return representation


class BuyersSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = AuthModels.ClientProfile
        fields = "__all__"


class _StoreSerializer(serializers.RelatedField, StoreSerializer):
    def to_internal_value(self, data):
        return self.queryset.get(name=data).pk

    def to_representation(self, value):
        return {"name": value.name, "slug": value.slug}

class CustomDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if isinstance(value, datetime):
            return value.date()
        return super().to_representation(value)

class PricingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductPrice
        fields = "__all__"

class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductColor
        fields = "__all__"

class ProductMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductMaterial
        fields = "__all__"

    
class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductTag
        fields = "__all__"

class ProductsSerializer(serializers.ModelSerializer):
    # store = _StoreSerializer(queryset=SupplierModels.Store.admin_list.all(), many=True, required=False)
    sub_category = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.ProductSubCategory.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=AuthModels.Supplier.objects.all(), required=False)
    created_on = CustomDateField()

    class Meta:
        model = SupplierModels.Product
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.supplier:
            if instance.store.all():
                supplier_data = SuppliersSerializer(
                    instance.store.all().first().supplier.profile
                ).data
            else:
                supplier_data = SuppliersSerializer(instance.supplier).data
            representation["supplier"] = supplier_data.get("business_name")
            representation["supplier_slug"] = supplier_data.get("slug")

        images = SupplierModels.ProductImage.objects.filter(product=instance)
        if images:
            representation["image"] = ProductImagesSerializer(
                images.first()
            ).data.get("image")

        representation["store"] = StoreSerializer(instance.stores, many=True).data
        
        sub_category = ProductSubCategorySerializer(SupplierModels.ProductSubCategory.objects.filter(pk=instance.sub_category.id).first()).data
        representation["sub_category"] = sub_category

        # pricings
        representation["pricings"] = PricingSerializer(SupplierModels.ProductPrice.objects.filter(product = instance), many=True).data
        representation["tags"] = ProductColorSerializer(SupplierModels.ProductTag.objects.filter(product = instance), many=True).data
        representation["colors"] = ProductMaterialSerializer(SupplierModels.ProductColor.objects.filter(product = instance), many=True).data
        representation["materials"] = ProductTagSerializer(SupplierModels.ProductMaterial.objects.filter(product = instance), many=True).data

        # images
        representation["images"] = ProductImagesSerializer(SupplierModels.ProductImage.objects.filter(product = instance), many=True).data
        representation["videos"] = ProductVideosSerializer(SupplierModels.ProductVideo.objects.filter(product = instance), many=True).data

        
        return representation


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductImage
        fields = "__all__"

class ProductVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.ProductVideo
        fields = "__all__"


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierModels.Service
        fields = "__all__"


class ContractReciptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModels.ContractReceipt
        fields = "__all__"


class ContractsSerializer(serializers.ModelSerializer):
    supplier = UserSerializer()
    buyer = UserSerializer()
    service = ServiceSerializer()

    class Meta:
        model = PaymentModels.Contract
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["receipt"] = ContractReciptSerializer(
            PaymentModels.ContractReceipt.objects.filter(contract=instance).first()
        ).data
        return representation


class LocationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerModels.Location
        fields = "__all__"


class ManagerServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerModels.Service
        fields = "__all__"


class ShowroomsSerializer(serializers.ModelSerializer):
    location = LocationsSerializer()
    store = _StoreSerializer(queryset=SupplierModels.Store.admin_list.all(), many=True)

    class Meta:
        model = ManagerModels.Showroom
        fields = "__all__"

    def to_representation(self, instance):
        product_count = 0
        representation = super().to_representation(instance)
        for store in instance.store.all():
            product_count = product_count + store.store_product.all().count()

        representation["products"] = product_count
        return representation


class MembershipReciptSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModels.MembershipReceipt
        fields = "__all__"


class MembershipSerializer(serializers.ModelSerializer):
    client = UserSerializer()

    class Meta:
        model = PaymentModels.Membership
        fields = "__all__"
        depth = 1

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["profile"] = instance.client.profile.business_name
        return representation

class AdvertsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerModels.Advert
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        product = SupplierModels.Product.admin_list.filter(id = representation["product"]).first()
        supplier_data = SuppliersSerializer(
            product.store.all().first().supplier.profile
        ).data
        representation["product"] = product.name
        representation["supplier"] = supplier_data.get("business_name")
        
        return representation

class CalenderEventserializer(serializers.ModelSerializer):
    # start_date = CustomDateField()
    # end_date = CustomDateField()
    business = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())

    class Meta:
        model = ManagerModels.CalenderEvent
        fields = "__all__"


class Orderserializer(serializers.ModelSerializer):
    buyer = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())
    supplier = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())
    delivery_date = CustomDateField()
    created_on = CustomDateField()
    accepted_on = CustomDateField()

    class Meta:
        model = SupplierModels.Order
        fields = "__all__"

class ProductVariationserializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.Order.objects.all())
    cart = serializers.PrimaryKeyRelatedField(queryset=BuyerModels.Cart.objects.all())
    product = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.Product.objects.all())
    price = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.ProductPrice.objects.all())
    color = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.ProductColor.objects.all())
    material = serializers.PrimaryKeyRelatedField(queryset=SupplierModels.ProductMaterial.objects.all())

    class Meta:
        model = SupplierModels.OrderProductVariation
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    target = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())
    class Meta:
        model = ManagerModels.Notification
        fields = "__all__"


class InterClientChatSerializer(serializers.ModelSerializer):
    initiator = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())
    participant = serializers.PrimaryKeyRelatedField(queryset=AuthModels.ClientProfile.objects.all())
    class Meta:
        model = ComsModels.InterClientChat
        fields = "__all__"

    
class InterUserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComsModels.InterUserChat
        fields = "__all__"

        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        participants = []
        for participant in instance.participants.all():
            participants.append(participant.pk)
        representation["participants"] = participants
        
        return representation

class GroupChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComsModels.GroupChat
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        participants = []
        for participant in instance.participants.all():
            participants.append(participant.pk)
        representation["participants"] = participants
        
        return representation