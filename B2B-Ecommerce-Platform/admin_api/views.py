from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from admin_api import serializers

from django.utils.translation import gettext as _

from auth_app import models as AuthModels
from supplier import models as SupplierModels
from buyer import models as BuyerModels
from manager import models as ManagerModels
from payment import models as PaymentModels

from manager import tasks as ManagerTasks


from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


class CustomListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class SupplierListView(ListAPIView):
    queryset = AuthModels.ClientProfile.objects.filter(
        user__account_type="SUPPLIER"
    ).order_by("-id")
    serializer_class = serializers.SuppliersSerializer
    pagination_class = CustomListPagination


class SupplierRetrieveView(RetrieveAPIView):
    queryset = AuthModels.ClientProfile.objects.filter(
        user__account_type="SUPPLIER"
    ).order_by("-id")
    serializer_class = serializers.SuppliersSerializer
    lookup_field = "slug"


class BuyersListView(ListAPIView):
    queryset = AuthModels.ClientProfile.objects.filter(
        user__account_type="BUYER"
    ).order_by("-id")
    serializer_class = serializers.BuyersSerializer
    pagination_class = CustomListPagination


class BuyerRetrieveView(RetrieveAPIView):
    queryset = AuthModels.ClientProfile.objects.filter(
        user__account_type="BUYER"
    ).order_by("-id")
    serializer_class = serializers.BuyersSerializer
    lookup_field = "slug"


class ProductsListView(ListAPIView):
    queryset = SupplierModels.Product.admin_list.all().order_by("-id")
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination


class ProductRetrieveView(RetrieveAPIView):
    queryset = SupplierModels.Product.admin_list.all().order_by("-id")
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"


class ProductDeleteView(APIView):
    def post(self, request, slug):
        try:
            product = SupplierModels.Product.admin_list.filter(slug=slug).first()
            product.is_verified = False
            product.save()

            # get supplier
            supplier = product.store.all().first().supplier

            # send mail
            ManagerTasks.send_mail.delay(
                subject = _("Suspension of Product On Foroden"),
                content = f"""
                    Dear {supplier.profile},

                    We regret to inform you that your product: {product} has been suspended on our website due to a violation of our Terms and Conditions. We have taken the necessary action to suspend it until the issue is rectified.

                    We request you to kindly contact our support team at {settings.SUPPORT_EMAIL} or use the website support feature to discuss the matter and find a way to bring your product back to our website. Our support team will guide you through the necessary steps to rectify the issue and make your product compliant with our guidelines.

                    We understand the inconvenience that this suspension may cause you and we apologize for the same. However, we believe that this action is necessary to ensure the quality and integrity of our platform and the all its products.

                    Please feel free to contact us if you have any questions or concerns regarding the suspension of your product. We appreciate your understanding and cooperation in this matter.

                    Thank you for your attention to this matter.

                    Sincerely,

                    Foroden.
                """,
                _to = [f"{supplier.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductVerifyView(APIView):
    def post(self, request, slug):
        try:
            product = SupplierModels.Product.admin_list.filter(slug=slug).first()
            product.is_verified = True
            product.save()

            
            supplier = product.store.all().first().supplier

            # send mail
            ManagerTasks.send_mail.delay(
                subject = _("Verification of Product On Foroden"),
                content = f"""
                    Dear {supplier.profile},

                    We are pleased to inform you that your product: {product} has been successfully verified and is now visible to all buyers on our website. Our team has thoroughly reviewed the product and found it to be compliant with our quality standards and guidelines.

                    We request you to kindly contact our support team at {settings.SUPPORT_EMAIL} or use the website support feature to discuss the matter.

                    We appreciate your patience and cooperation during the verification process. We understand that this may have caused inconvenience to you, but we assure you that this step was necessary to ensure that all products on our website meet our quality standards and guidelines.

                    Please feel free to contact us if you have any questions or concerns regarding the verification of your product. We are always available to assist you in any way we can.

                    Thank you for choosing our platform to sell your products. We look forward to a successful and long-term partnership with you.

                    Sincerely,

                    Foroden.
                """,
                _to = [f"{supplier.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

        except Exception as Err:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class SupplierProductsListView(ListAPIView):
    serializer_class = serializers.ProductsSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"

    def get_queryset(self):
        supplier = AuthModels.ClientProfile.objects.filter(
            slug=self.kwargs.get("slug")
        ).first()

        queryset = SupplierModels.Product.admin_list.filter(store__supplier=supplier.user)

        return queryset


class ProductImageListView(ListAPIView):
    serializer_class = serializers.ProductImagesSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"

    def get_queryset(self):
        product = SupplierModels.Product.admin_list.filter(
            slug=self.kwargs.get("slug")
        ).first()

        queryset = SupplierModels.ProductImage.objects.filter(
            product=product
        ).order_by()

        return queryset


class ContractsListView(ListAPIView):
    queryset = PaymentModels.Contract.objects.all().order_by("-id")
    serializer_class = serializers.ContractsSerializer
    pagination_class = CustomListPagination


class ContractRetrieveView(RetrieveAPIView):
    queryset = PaymentModels.Contract.objects.all().order_by("-id")
    serializer_class = serializers.ContractsSerializer
    pagination_class = CustomListPagination
    lookup_field = "id"


class ShowroowListView(ListAPIView):
    queryset = ManagerModels.Showroom.objects.all().order_by("-id")
    serializer_class = serializers.ShowroomsSerializer
    pagination_class = CustomListPagination


class ShowroowRetrieveView(RetrieveAPIView):
    queryset = ManagerModels.Showroom.objects.all().order_by("-id")
    serializer_class = serializers.ShowroomsSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"


class SupplierShowroowListView(ListAPIView):
    queryset = ManagerModels.Showroom.objects.all().order_by("-id")
    serializer_class = serializers.ShowroomsSerializer

    def get_queryset(self):
        supplier = AuthModels.ClientProfile.objects.filter(
            slug=self.kwargs.get("slug")
        ).first()

        queryset = ManagerModels.Showroom.objects.filter(
            store__in=supplier.user.store_set.all().order_by("-id")
        )

        return queryset


class ManagerServicesListView(ListAPIView):
    queryset = ManagerModels.Service.objects.all().order_by("-id")
    serializer_class = serializers.ManagerServicesSerializer
    pagination_class = CustomListPagination


class ManagerServiceRetrieveView(RetrieveAPIView):
    queryset = ManagerModels.Service.objects.all().order_by("-id")
    serializer_class = serializers.ManagerServicesSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"


class MembershipListView(ListAPIView):
    queryset = PaymentModels.Membership.objects.all().order_by("-id")
    serializer_class = serializers.MembershipSerializer
    pagination_class = CustomListPagination


class StoreListView(ListAPIView):
    queryset = SupplierModels.Store.admin_list.all().order_by("-id")
    serializer_class = serializers.StoreSerializer
    pagination_class = CustomListPagination


class StoreRetrieveView(RetrieveAPIView):
    queryset = SupplierModels.Store.admin_list.all().order_by("-id")
    serializer_class = serializers.StoreSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"


class SupplierStoresListView(ListAPIView):
    queryset = SupplierModels.Store.admin_list.all().order_by("-id")
    serializer_class = serializers.StoreSerializer
    pagination_class = CustomListPagination

    def get_queryset(self):
        supplier = AuthModels.ClientProfile.objects.filter(
            slug=self.kwargs.get("slug")
        ).first()

        queryset = SupplierModels.Store.admin_list.filter(supplier=supplier.user)

        return queryset

class StoreDeleteView(APIView):
    def post(self, request, slug):
        try:
            store = SupplierModels.Store.admin_list.filter(slug=slug).first()
            store.is_verified = False
            store.save()


            supplier = store.supplier

            # send mail
            ManagerTasks.send_mail.delay(
                subject = _("Suspension of Store On Foroden"),
                content = f"""
                    Dear {supplier.profile},

                    We regret to inform you that your store: {store} has been suspended on our website due to a violation of our Terms and Conditions. We have taken the necessary action to suspend it until the issue is rectified.

                    We request you to kindly contact our support team at {settings.SUPPORT_EMAIL} or use the website support feature to discuss the matter and find a way to bring your store back to our website. Our support team will guide you through the necessary steps to rectify the issue and make your store compliant with our guidelines.

                    We understand the inconvenience that this suspension may cause you and we apologize for the same. However, we believe that this action is necessary to ensure the quality and integrity of our platform and the all its stores.

                    Please feel free to contact us if you have any questions or concerns regarding the suspension of your store. We appreciate your understanding and cooperation in this matter.

                    Thank you for your attention to this matter.

                    Sincerely,

                    Foroden.
                """,
                _to = [f"{supplier.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class StoreVerifyView(APIView):
    def post(self, request, slug):
        try:
            store = SupplierModels.Store.admin_list.filter(slug=slug).first()
            store.is_verified = True
            store.save()

            supplier = store.supplier

            # send mail
            ManagerTasks.send_mail.delay(
                subject = _("Verification of Store On Foroden"),
                content = f"""
                    Dear {supplier.profile},

                    We are pleased to inform you that your store: {store} has been successfully verified and is now visible to all buyers on our website. Our team has thoroughly reviewed the store and found it to be compliant with our quality standards and guidelines.

                    We request you to kindly contact our support team at {settings.SUPPORT_EMAIL} or use the website support feature to discuss the matter.

                    We appreciate your patience and cooperation during the verification process. We understand that this may have caused inconvenience to you, but we assure you that this step was necessary to ensure that all stores on our website meet our quality standards and guidelines.

                    Please feel free to contact us if you have any questions or concerns regarding the verification of your store. We are always available to assist you in any way we can.

                    Thank you for choosing our platform to sell your stores. We look forward to a successful and long-term partnership with you.

                    Sincerely,

                    Foroden.
                """,
                _to = [f"{supplier.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

        except Exception as Err:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)



class ServicesListView(ListAPIView):
    queryset = ManagerModels.Service.objects.all().order_by("-id")
    serializer_class = serializers.ManagerServicesSerializer
    pagination_class = CustomListPagination


class ServiceRetrieveView(RetrieveAPIView):
    queryset = ManagerModels.Service.objects.all().order_by("-id")
    serializer_class = serializers.ManagerServicesSerializer
    pagination_class = CustomListPagination
    lookup_field = "slug"


class SuspendAccountView(APIView):
    def post(self, request, slug):
        try:
            user = AuthModels.ClientProfile.objects.filter(slug=slug).first().user

            # not working
            user.is_active = False
            user.save()

            # send mail
            ManagerTasks.send_mail.delay(
                subject = _("Suspension of Store On Foroden"),
                content = f"""
                    Dear {supplier.profile},

                    We regret to inform you that your account has been suspended on our website until further notice. Our team has identified some issues with your account that do not comply with our Terms and Conditions, and we have taken the necessary action to suspend your account until the issue is rectified.

                    We request you to kindly contact our support team at {settings.SUPPORT_EMAIL} or use the website support feature to discuss the matter and find a way to reactivate your account. Our support team will guide you through the necessary steps to rectify the issue and make your account compliant with our guidelines.

                    We understand the inconvenience that this suspension may cause you and we apologize for the same. However, we believe that this action is necessary to ensure the quality and integrity of our platform and the user accounts on it.

                    Please feel free to contact us if you have any questions or concerns regarding the suspension of your account. We appreciate your understanding and cooperation in this matter.

                    Thank you for your attention to this matter.

                    Sincerely,

                    Foroden.
                """,
                _to = [f"{supplier.email}"],
                _reply_to = [f"{settings.SUPPORT_EMAIL}"]
            )

            return Response(status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class AdvertsListView(ListAPIView):
    queryset = ManagerModels.Advert.objects.all().order_by("-id")
    serializer_class = serializers.AdvertsSerializer
    pagination_class = CustomListPagination