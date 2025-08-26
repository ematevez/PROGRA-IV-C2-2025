from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.views.generic import ListView
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from django.contrib import messages
from datetime import datetime
from django.utils import timezone
from django.db.models import Count

from auth_app import models as AuthModels
from payment import models as PaymentModels
from supplier import models as SupplierModels
from buyer import models as BuyerModels
from manager import models as ManagerModels
from coms import models as ComsModels

from buyer import tasks as BuyerTasks

from buyer.mixins import BuyerOnlyAccessMixin

from django.utils.translation import get_language
from googletrans import Translator
from django.conf import settings

import random

translator = Translator()

from auth_app import forms as AuthForms


class ProfileView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/profile.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = _("Profile")
        context_data["buyer"] = AuthModels.Buyer.buyer.filter(
            id=self.request.user.id
        ).first()

        return context_data


class EditAccountsProfileView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/account_edit.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        if not (
            request.POST.get("first_name")
            and request.POST.get("last_name")
            and request.POST.get("username")
            and request.POST.get("email")
        ):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))

        if (
            request.POST.get("first_name") == request.user.first_name
            and request.POST.get("last_name") == request.user.last_name
            and request.POST.get("username") == request.user.username
            and request.POST.get("email") == request.user.email
        ):
            messages.add_message(
                request, messages.ERROR, _("No modification was made.")
            )
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))

        if (
            AuthModels.User.objects.filter(username=request.POST.get("username"))
            and request.POST.get("username") != request.user.username
        ):
            messages.add_message(request, messages.ERROR, _("Username not available."))
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))

        if (
            AuthModels.User.objects.filter(email=request.POST.get("email"))
            and request.POST.get("email") != request.user.email
        ):
            messages.add_message(request, messages.ERROR, _("Email not available."))
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))

        form = AuthForms.UserUpdateFormManager(data=request.POST, instance=request.user)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, _("Invalid data. Try again."))
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))
        form.save()

        fields = ("first_name", "last_name")
        instance = request.user
        modal = AuthModels.User
        for field in fields:
            for language in settings.LANGUAGES:
                try:
                    if language[0] == get_language():
                        # already set
                        continue
                    result = translator.translate(
                        getattr(instance, field), dest=language[0]
                    )
                    for model_field in modal._meta.get_fields():
                        if not model_field.name in f"{field}_{language[0]}":
                            continue

                        if model_field.name == f"{field}_{language[0]}":
                            setattr(instance, model_field.name, result.text)
                            instance.save()
                except:
                    setattr(
                        instance, f"{field}_{language[0]}", getattr(instance, field)
                    )
                    instance.save()
        messages.add_message(
            request, messages.SUCCESS, _("Account Details Editted Successfully")
        )
        return redirect(reverse("buyer:profile"))


def password_reset(request):
    if request.method == "GET":
        return render(request, "buyer/dashboard/password_reset.html")

    if request.method == "POST":
        if request.POST.get("new_password") != request.POST.get("confirm_new_password"):
            messages.add_message(request, messages.ERROR, _("Password mismatch."))
            return redirect(reverse("buyer:password-reset"))

        # confirm current password
        user = authenticate(
            username=request.user.username,
            password=request.POST.get("current_password"),
        )
        if not user:
            messages.add_message(
                request, messages.ERROR, _("Wrong current password entered.")
            )
            return redirect(reverse("buyer:password-reset"))

        if authenticate(
            username=request.user.username, password=request.POST.get("new_password")
        ):
            messages.add_message(request, messages.ERROR, _("No modification made."))
            return redirect(reverse("buyer:password-reset"))

        # make password
        generated_password = make_password(request.POST.get("new_password"))
        user = AuthModels.User.objects.filter(pk=request.user.pk).first()
        user.password = generated_password
        user.save()
        messages.add_message(
            request, messages.SUCCESS, _("Account password reset successfully")
        )
        return redirect(reverse("buyer:profile"))


class BusinessProfileView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/business-profile.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = _("Profile")
        context_data["buyer"] = AuthModels.Buyer.buyer.filter(
            id=self.request.user.id
        ).first()

        return context_data


class EditBusinessProfileView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/business_edit.html"

    def get(self, request, slug):
        context_data = {
            "profile": AuthModels.ClientProfile.objects.filter(slug=slug).first()
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, slug):
        profile = AuthModels.ClientProfile.objects.filter(slug=slug).first()
        required_fields = [
            request.POST.get("business_name", None),
            request.POST.get("business_description", None),
            request.POST.get("country", None),
            request.POST.get("city", None),
        ]

        if None in required_fields:
            messages.add_message(
                request,
                messages.ERROR,
                "{}".format(_("Please Fill all reqiured fields.")),
            )
            return redirect(reverse("buyer:dashboard-editbusinessprofile", args=[slug]))

        try:
            form = AuthForms.UserProfileUpdateFormManager(
                data=request.POST, instance=profile
            )
            if not form.is_valid():
                messages.add_message(
                    request, messages.ERROR, _("Invalid data. Try again.")
                )
                return redirect(reverse("buyer:dashboard-editaccountsprofile"))
            form.save()

            fields = (
                "business_name",
                "business_description",
                "country",
                "country_code",
                "city",
                "mobile_user",
            )
            instance = profile
            modal = AuthModels.ClientProfile
            for field in fields:
                for language in settings.LANGUAGES:
                    try:
                        if language[0] == get_language():
                            # already set
                            continue
                        result = translator.translate(
                            getattr(instance, field), dest=language[0]
                        )
                        for model_field in modal._meta.get_fields():
                            if not model_field.name in f"{field}_{language[0]}":
                                continue

                            if model_field.name == f"{field}_{language[0]}":
                                setattr(instance, model_field.name, result.text)
                                instance.save()
                    except:
                        setattr(
                            instance, f"{field}_{language[0]}", getattr(instance, field)
                        )
                        instance.save()

            messages.add_message(
                request, messages.SUCCESS, _("Business Details Editted Successfully.")
            )
            return redirect(reverse("buyer:business"))
        except Exception as e:
            print(e)
            messages.add_message(
                request, messages.ERROR, _("An Error Occurred. Try Again.")
            )
            return redirect(reverse("buyer:dashboard-editbusinessprofile", args=[slug]))


class ContractListView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/contracts.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = _("Contracts")
        context_data["contracts"] = PaymentModels.ContractReceipt.objects.filter(
            contract__buyer=self.request.user
        )

        return context_data

class OrdersView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/orders.html"

    def get(self, request):
        return render(request, self.template_name)


class RequestForQuoteView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/request-for-quote.html"

    def get(self, request):
        return render(request, self.template_name)


class OrderHistoryView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/order-history.html"

    def get(self, request):
        return render(request, self.template_name)

class DashboardView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/dashboard.html"

    def get(self, request):
        context_data = {}
        context_data["orders"] = [
            obj
            for obj in SupplierModels.Order.objects.filter(buyer=request.user.business)
            .values("status")
            .annotate(dcount=Count("status"))
            .order_by()
        ]
        return render(request, self.template_name, context=context_data)


class CalendarView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/calendar.html"

    def get(self, request):
        return render(request, self.template_name)


class NotificationsView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/notifications.html"

    def get(self, request):
        return render(request, self.template_name)

class BidsView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/bids.html"

    def get(self, request):
        return render(request, self.template_name)


class BidsCompareView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/bids-compare.html"

    def get(self, request):
        return render(request, self.template_name)

class BidsView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/bids.html"

    def get(self, request):
        return render(request, self.template_name)

class ReportingAnalyticsView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/reporting-analytics.html"

    def get(self, request):
        return render(request, self.template_name)

class VisitedProductsListView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/products.html"

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())

    def get_context_data(self):
        context_data = dict()

        context_data["view_name"] = _("Contracts")
        context_data["contracts"] = ""

        return context_data


class DashboardContractsDetailsView(View):
    template_name = "buyer/dashboard/contract-detail.html"
    model = PaymentModels.Contract

    def get(self, request, pk):
        contract = PaymentModels.Contract.objects.filter(pk=pk).first()
        context_data = {
            "contract": contract,
            "receipt": PaymentModels.ContractReceipt.objects.filter(
                contract=contract
            ).first(),
        }
        return render(request, self.template_name, context=context_data)





#---------------------------------------- WishList ----------------------------------------
class WishListListView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/wishlist.html"
    model = SupplierModels.WishListProduct

    def get_queryset(self):
        business = AuthModels.ClientProfile.objects.filter(user = self.request.user)
        return self.model.objects.filter(buyer=business.first())

# @method_decorator(csrf_exempt, name='dispatch')
class WishListAppeendAppendView(BuyerOnlyAccessMixin, View):
    model = SupplierModels.WishListProduct

    def post(self, request, product_slug):
        product = get_object_or_404(SupplierModels.Product, slug=product_slug)
        business = AuthModels.ClientProfile.objects.filter(user = self.request.user)
        
        self.model.objects.create(
            buyer = business.first(),
            product = product
        )
        return redirect(reverse("buyer:wishlist"))

# @method_decorator(csrf_exempt, name='dispatch')
class WishListDeleteProductView(BuyerOnlyAccessMixin, View):
    model = SupplierModels.WishListProduct

    def post(self, request, product_slug):
        product = get_object_or_404(SupplierModels.Product, slug=product_slug)
        business = AuthModels.ClientProfile.objects.filter(user = self.request.user)
        
        wishlist_product = self.model.objects.filter(product = product, buyer=business.first())
        if wishlist_product:
            wishlist_product.first().delete()
        return redirect(reverse("buyer:wishlist"))

# cart
class CartListView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/cartlist.html"
    model = BuyerModels.Cart

    def get_queryset(self):
        business = AuthModels.ClientProfile.objects.filter(user=self.request.user).first()
        cart = self.model.objects.filter(buyer=business)
        if not cart:
            cart = BuyerModels.Cart.objects.create(buyer=business)
        else:
            cart = cart.first()

        return SupplierModels.OrderProductVariation.objects.filter(cart=cart)


# @method_decorator(csrf_exempt, name='dispatch')
class CartDeleteProductView(BuyerOnlyAccessMixin, View):
    def post(self, request, pk):
        product_variation = get_object_or_404(SupplierModels.OrderProductVariation, pk=pk)
        product_variation.delete()
        return redirect(reverse("buyer:cart-list"))

class OrderCreateView(BuyerOnlyAccessMixin, View):
    def post(self, request):
        business = AuthModels.ClientProfile.objects.filter(user = self.request.user).first()
        cart = BuyerModels.Cart.objects.filter(buyer=business)
        if not cart:
            messages.add_message(request, messages.ERROR, _("No Products found in Cart."))
            return redirect(reverse("buyer:cart-list"))

        product_variations = SupplierModels.OrderProductVariation.objects.filter(cart=cart.first())
        if not product_variations:
            messages.add_message(request, messages.ERROR, _("No Products found in Cart."))
            return redirect(reverse("buyer:cart-list"))

        groupings = {}
        for product_variation in product_variations:
            supplier = product_variation.product.supplier
            if not groupings.get(supplier):
                groupings[supplier] = []
            groupings[supplier].append(product_variation)

        # create orders to the different suppliers
        for bus, prods in groupings.items():
            order = SupplierModels.Order.objects.create(
                buyer = business,
                supplier = bus
            )
            for prod in prods:
                prod.order = order
                prod.cart = None
                prod.save()

            SupplierModels.OrderShippingDetail.objects.create(order=order)
            
            # notify suppliers
            BuyerTasks.order_placed_notify_supplier.delay(order.pk, instance.__class__.__name__)
        
        messages.add_message(request, messages.SUCCESS, _("Orders Placed successfully. Adjust Order Details."))
        return redirect(reverse("buyer:order-tracking"))



class OrderTrackingView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/order-tracking.html"
    model = SupplierModels.Order
    PER_PAGE_COUNT = 20

    def get(self, request):

        return render(
            request, template_name=self.template_name, context=self.get_context_data()
        )

    def get_queryset(self):
        # filters => creation date, delivery date, overdue, new, buyer
        self.queryset = self.model.objects.filter(buyer = self.request.user.business)

        supplier_slug = self.request.GET.get("supplier", 0)
        country_name = self.request.GET.get("country", 0)
        if supplier_slug:
            supplier = get_object_or_404(AuthModels.ClientProfile, slug=supplier_slug)
            self.queryset = self.queryset.filter(supplier = supplier)
            
        if self.request.GET.get("overdue", 0):
            today = timezone.now().date()
            self.queryset = self.queryset.filter(delivery_date__lt=today)

        if country_name:
            self.queryset = self.queryset.filter(supplier__country=country_name)
            
        if self.request.GET.get("status", 0):
            if self.request.GET.get("status", 0) != "ALL":
                self.queryset = self.queryset.filter(status=self.request.GET.get("status", 0))

        if self.request.GET.get("order_search_value", 0):
            order_search_value = self.request.GET.get("order_search_value", 0)
            self.queryset = self.queryset.filter(Q(order_id=order_search_value) | Q(supplier__business_name__icontains=order_search_value))

        return self.queryset

    def get_paginator(self):

        queryset = self.get_queryset()
        self.records = queryset.order_by("-updated_on")
        paginator = Paginator(self.records, self.PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):
        context_data = dict()

        paginator = self.get_paginator()

        context_data["view_name"] = _("Order")
        context_data["page_obj"] = paginator
        context_data["item_count"] = len(self.records)
        context_data["current_page_number"] = self.request.GET.get("page", 1)

        context_data["orders"] = {
            "context-name": "orders",
            "results": paginator.object_list,
        }

        context_data["suppliers"] = {
            "context_name": "suppliers",
            "results": {order.supplier for order in self.model.objects.filter(buyer = self.request.user.business)}
        }
        context_data["countries"] = {
            "context_name": "countries",
            "results": {order.supplier.country for order in self.model.objects.filter(buyer = self.request.user.business)}
        }
        context_data["statuses"] = {
            "context_name": "statuses",
            "results": [status[0] for status in SupplierModels.Order.order_statuses]
        }
        
        return context_data


class OrderDetaliView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/order-details.html"
    model = SupplierModels.Order

    def get(self, request, order_id):
        order = get_object_or_404(self.model, order_id=order_id)

        if order.buyer.user != request.user:
            return redirect(reverse("buyer:order-tracking"))

        order_notes = SupplierModels.OrderNote.objects.filter(user=request.user, order=order)
        if order_notes:
            order_notes = order_notes.first()

        shipping_details = SupplierModels.OrderShippingDetail.objects.filter(order=order)
        if shipping_details:
            shipping_details = shipping_details.first()

        context_data = {
            "order" : order,
            "order_products" : SupplierModels.OrderProductVariation.objects.filter(order=order),
            "order_notes" : order_notes,
            "shipping_details" : shipping_details,
            "order_chat": ComsModels.OrderChat.objects.filter(order=order)
        }
        return render(
            request, template_name=self.template_name, context=context_data
        )

    def post(self, request, order_id):
        order = get_object_or_404(self.model, order_id=order_id)

        if order.buyer.user != request.user:
            return redirect(reverse("buyer:order-tracking"))

        if request.POST.get("order_notes"):
            order_notes = request.POST.get("order_notes")
            if SupplierModels.OrderNote.objects.filter(user=request.user, order=order):
                note = SupplierModels.OrderNote.objects.filter(user=request.user, order=order).first()
            else:
                note = SupplierModels.OrderNote.objects.create(user=request.user, order=order)
            note.notes = order_notes
            note.save()

        if request.POST.get("delivery_date"):
            date = request.POST.get("delivery_date")
            order.delivery_date = date
            order.save()
            BuyerTasks.notify_suppleir_form_buyer.delay(order.order_id, "DELIVERY_DATE_SET")
        
        if request.POST.get("currency") and request.POST.get("agreed_price"):
            currency = request.POST.get("currency")
            agreed_price = float(request.POST.get("agreed_price"))
            order.currency = currency
            order.agreed_price = agreed_price
            order.save()
            BuyerTasks.notify_suppleir_form_buyer.delay(order.order_id, "AGREED_PRICE_SET")

            # add to calender
            ManagerModels.CalenderEvent.objects.create(
                business = order.supplier,
                title = "Order {} Delivery.".format(order.order_id),
                start = order.delivery_date
            )
            ManagerModels.CalenderEvent.objects.create(
                business = order.buyer,
                title = "Order {} Delivery.".format(order.order_id),
                start = order.delivery_date
            )

        return redirect(reverse("buyer:order-detail", kwargs={"order_id": order.order_id}))


class ProductVariationDetails(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/order-product-details.html"
    model = SupplierModels.OrderProductVariation

    def get(self, request, pk):
        variation = get_object_or_404(self.model, pk=pk)

        if variation.order.buyer.user != request.user:
            return redirect(reverse("buyer:order-tracking"))

        context_data = {
            "object" : variation,
            "colors" : SupplierModels.ProductColor.objects.filter(product = variation.product),
            "materials" : SupplierModels.ProductMaterial.objects.filter(product = variation.product),
            "pricings" : SupplierModels.ProductPrice.objects.filter(product = variation.product)
        }
        return render(
            request, template_name=self.template_name, context=context_data
        )

    def post(self, request, pk):
        variation = get_object_or_404(self.model, pk=pk)

        if variation.order.buyer.user != request.user:
            return redirect(reverse("buyer:order-tracking"))

        if request.POST.get("delete") == "Delete Product":
            variation.delete()
            messages.add_message(request, messages.SUCCESS, _("Product removed successfully."))
            return redirect(reverse("buyer:order-detail", kwargs={"order_id": variation.order.order_id}))
        
        if request.POST.get("edit") == "Save Details":
            product_color_pk = request.POST.get("product_color")
            product_material_pk = request.POST.get("product_material")
            product_pricing_pk = request.POST.get("product_pricing")
            product_quantity = request.POST.get("product_quantity")

            if int(product_quantity) < 1:
                messages.add_message(request, messages.ERROR, _("Invalid Product Quantity."))
                return redirect(reverse("buyer:product-variation-detial", kwargs={"pk": variation.pk}))

            if product_color_pk:
                variation.color = SupplierModels.ProductColor.objects.filter(pk=product_color_pk).first()

            if product_material_pk:
                variation.material = SupplierModels.ProductMaterial.objects.filter(pk=product_material_pk).first()

            if product_pricing_pk:
                variation.price = SupplierModels.ProductPrice.objects.filter(pk=product_pricing_pk).first()

            variation.quantity = product_quantity
            variation.save()
        
            BuyerTasks.notify_suppleir_form_buyer.delay(variation.order.order_id, "PRODUCT_DETAILS_UPDATED")
            messages.add_message(request, messages.SUCCESS, _("Product Details Edited successfully."))
            return redirect(reverse("buyer:order-detail", kwargs={"order_id": variation.order.order_id}))

class OrderAddProductView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/order-product-add.html"
    model = SupplierModels.Order
    PER_PAGE_COUNT = 20

    def get(self, request, order_id):

        return render(
            request, template_name=self.template_name, context=self.get_context_data(order_id=order_id)
        )

    def get_queryset(self):

        # get query parameters
        search = self.request.GET.get("search", None)
        if search:
            # we are searching for products based on name, sub category, category, tag
            return SupplierModels.Product.objects.filter(
                Q(name__icontains=search)
                | Q(sub_category__name__icontains=search)
                | Q(category__name__icontains=search)
                | Q(producttag__name__icontains=search)
            ).distinct("id")

        return SupplierModels.Product.objects.all()

    def get_products_paginator(self):

        queryset = self.get_queryset()

        self.products = random.sample(
            list(queryset.order_by("-id")),
            self.PER_PAGE_COUNT if queryset.count() >= 20 else queryset.count(),
        )

        paginator = Paginator(self.products, self.PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):
        context_data = dict()
        context_data["order"] = get_object_or_404(SupplierModels.Order, order_id=kwargs.get("order_id"))

        products_paginator = self.get_products_paginator()

        context_data["view_name"] = _("Products")
        context_data["page_obj"] = products_paginator
        context_data["product_count"] = len(self.products)
        context_data["current_page_number"] = self.request.GET.get("page", 1)

        context_data["products"] = {
            "context-name": "products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": product.productimage_set.all().first(),
                }
                for product in products_paginator.object_list
            ],
        }
        return context_data

    def post(self, request, order_id):
        order = get_object_or_404(SupplierModels.Order, order_id=order_id)
        product = get_object_or_404(SupplierModels.Product, slug=request.POST.get("new_product"))
        business = AuthModels.ClientProfile.objects.filter(user = self.request.user).first()

        # if SupplierModels.OrderProductVariation.objects.filter(product=product, order=order):
        #     messages.add_message(request, messages.ERROR, _("Product already exits in this order."))
        #     return redirect(reverse("buyer:order-detail", kwargs={"order_id": order.order_id}))


        variation = SupplierModels.OrderProductVariation(
            order=order,
            product=product,
            quantity=1
        )
        if variation:
            variation.save()
            BuyerTasks.notify_suppleir_form_buyer.delay(variation.order.order_id, "PRODUCT_ADDED_TO_ORDER")
            messages.add_message(request, messages.SUCCESS, _("Edit Product Details."))
            return redirect(reverse("buyer:product-variation-detial", kwargs={"pk": variation.pk}))
        else:
            messages.add_message(request, messages.ERROR, _("Please Try again."))
            return redirect(reverse("buyer:order-add-product", kwargs={"order_id": order.order_id}))

class OrderShippingDetailView(BuyerOnlyAccessMixin, View):
    template_name = "buyer/dashboard/order-shipping-details.html"

    def get(self, request, order_id):
        order = get_object_or_404(SupplierModels.Order, order_id=order_id)
        shipping  = SupplierModels.OrderShippingDetail.objects.filter(order=order)
        
        if not shipping:
            shipping = SupplierModels.OrderShippingDetail.objects.create(
                order = order,
            )
        else:
            shipping = shipping.first()

        context_data = {
            "object" : shipping,
            "carriers" : SupplierModels.DeliveryCarrier.objects.filter(active=True)
        }
        return render(
            request, template_name=self.template_name, context=context_data
        )

    def post(self, request, order_id):
        order = get_object_or_404(SupplierModels.Order, order_id=order_id)
        shipping  = SupplierModels.OrderShippingDetail.objects.filter(order=order).first()

        shipping.carrier = get_object_or_404(SupplierModels.DeliveryCarrier, pk=request.POST.get("carrier"))
        shipping.country = request.POST.get("country")
        shipping.city = request.POST.get("city")
        shipping.address_1 = request.POST.get("address_1")
        shipping.address_2 = request.POST.get("address_2")
        
        shipping.save()
        BuyerTasks.notify_suppleir_form_buyer.delay(order.order_id, "SHIPPING_DETAILS_UPDATED")
        messages.add_message(request, messages.SUCCESS, _("Shipping Details Updated."))
        return redirect(reverse("buyer:order-detail", kwargs={"order_id": order.order_id}))


class MessengerView(BuyerOnlyAccessMixin, ListView):
    template_name = "buyer/dashboard/messenger.html"

    def get(self, request):
        context_data = {
            "business_chat" : ComsModels.InterClientChat.objects.filter(
                Q(initiator=self.request.user.business)
                | Q(participant=self.request.user.business)
            ).first()
        }
        return render(request, self.template_name, context=context_data)