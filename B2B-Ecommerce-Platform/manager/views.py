from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
import random
from django.utils.translation import gettext as _
from django.contrib import messages
from django.utils import timezone

from datetime import timedelta
import uuid

# apps
from supplier.models import (
    Product,
    ProductCategory,
    Store,
    ProductImage,
    ProductSubCategory,
)
from manager import models as ManagerModels
from payment import models as PaymentModels

from manager import tasks as ManagerTasks


from payment.mixins import AuthedOnlyAccessMixin


from django.utils.translation import get_language
from googletrans import Translator
from django.conf import settings

translator = Translator()


class HomeView(View):
    template_name = "manager/index.html"

    def get(self, request):

        context_data = {
            "view_name": _("Home"),
            "product_categories": {
                "context_name": "product-categories",
                "results": [
                    {
                        "category": category,
                        "sub_categories": (
                            lambda sub_categories: random.sample(
                                sub_categories, len(sub_categories)
                            )
                        )(
                            list(
                                ProductSubCategory.objects.filter(
                                    category=category
                                ).order_by("-id")
                            )
                        )[
                            :3
                        ],
                    }
                    for category in (
                        lambda categories: random.sample(categories, len(categories))
                    )(list(ProductCategory.objects.all().order_by("-id")))[:6]
                ],
            },
            "showrooms": {
                "context_name": "showrooms",
                "results": ManagerModels.Showroom.objects.all().order_by("-id")[:6],
            },
            "new_arrivals": {
                "context_name": "new-arrivals",
                "results": [
                    {
                        "product": product,
                        "main_image": ProductImage.objects.filter(
                            product=product
                        ).first(),
                    }
                    for product in Product.objects.all().order_by("-id")[:12]
                ],
            },
            "products": {
                "context_name": "products",
                "results": [
                    {
                        "product": product,
                        "supplier": product.store.all().first().supplier,
                        "images": ProductImage.objects.filter(product=product).first(),
                    }
                    for product in (
                        lambda products: random.sample(products, len(products))
                    )(list(Product.objects.all().order_by("-id")[:12]))
                ],
            },
            "stores": {
                "context_name": "stores",
                "results": Store.objects.all().distinct("supplier")[:6],
            },
            "banners": {
                "context_name": "banners",
                "results": ManagerModels.Promotion.objects.filter(has_image=True).order_by("-id")[:6]
            }
        }

        context_data["adverts"]  = {
            "context_name" : "adverts",
            "results": [
                {
                    "product": advert.product,
                    "supplier": advert.product.store.all().first().supplier,
                    "main_image": ProductImage.objects.filter(product=advert.product).first(),
                }
                for advert in (lambda adverts: random.sample(adverts, len(adverts)))(list(ManagerModels.Advert.active.all())[:3])
            ],
        }

        return render(request, self.template_name, context=context_data)


# showrooms
class ShowRoomListView(ListView):
    model = ManagerModels.Showroom

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["view_name"] = _("Showrooms")
        context["showrooms_with_products"] = {
            "context_name": "showrooms",
            "results": [
                {
                    "showroom": showroom,
                    "store_count": showroom.store.count(),
                    "banner" : ManagerModels.Promotion.objects.filter(showroom=showroom).order_by("-id").first(),
                    "products": [
                        {
                            "product": product,
                            "images": product.productimage_set.all().first(),
                        }
                        for product in (
                            lambda products: random.sample(products, len(products))
                        )(
                            [
                                product
                                for product in Product.objects.filter(
                                    store__in=showroom.store.all()
                                )
                            ][:3]
                        )
                    ],
                }
                for showroom in (
                    lambda showrooms: random.sample(showrooms, len(showrooms))
                )(list(ManagerModels.Showroom.objects.filter(store__gte=1).distinct("id")))
            ],
        }
        
        context["showrooms_without_products"] = {
            "context_name": "showrooms",
            "results": [
                {"showroom": showroom, "store_count": showroom.store.count()}
                for showroom in (
                    lambda showrooms: random.sample(showrooms, len(showrooms))
                )([showroom for showroom in ManagerModels.Showroom.objects.all() if showroom.store.all().count() < 1])
            ],
        }

        context["stores"] = {
            "context_name": "stores",
            "results": (lambda stores: random.sample(stores, len(stores)))(
                list(Store.objects.all()[:10])
            ),
        }
        return context


class ShowRoomDetailView(DetailView):
    model = ManagerModels.Showroom

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        showroom = self.get_object()

        showroom_products = [
            product for product in Product.objects.filter(store__in=showroom.store.all())
        ]

        context["view_name"] = showroom.name
        context["stores"] = {"context_name": "stores", "results": showroom.store.all()}
        context["other_showroom"] = {
            "context_name": "other-showroom",
            "results": [
                {"showroom": showroom, "store_count": showroom.store.count()}
                for showroom in (
                    lambda showrooms: random.sample(showrooms, len(showrooms))
                )(list(ManagerModels.Showroom.objects.filter(~Q(id=showroom.id))[:10]))
            ],
        }
        context["products"] = {
            "context_name": "products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": product.productimage_set.all().first(),
                }
                for product in (
                    lambda products: random.sample(products, len(products))
                )(
                    showroom_products[:20]
                )
            ],
        }

        context["banners"] = {
            "context_name": "banners",
            "results": ManagerModels.Promotion.objects.filter(has_image=True, showroom=showroom).order_by("-id")[:6]
        }

        try:
            ads = (
                        lambda ads: random.sample(ads, len(ads))
                    )(list(ManagerModels.Promotion.text_objects.filter(
                        ~Q(type="SHOWROOWS") | Q(showroom__pk = showroom.pk)
                    ).order_by("-id")[:10]))
        except:
            ads = (
                        lambda ads: random.sample(ads, len(ads))
                    )(list(ManagerModels.Promotion.text_objects.filter(
                        ~Q(type="SHOWROOWS") | Q(showroom__pk = showroom.pk)
                    ).order_by("-id")[:10]))

        context["text_promotion"] = {
            "context_name": "text_promotion",
            "results": ads[:3] if len(ads) > 0 else ads
        }

        product = (lambda products: random.sample(products, len(products)))(
            list(Product.objects.all().order_by("-id")[:10])
        )[0]

        context["category_group"] = {
            "context_name": "product-category-group",
            "category": product.category,
            "results": [
                {
                    "subcategory": subcategory,
                    "results": [
                        {
                            "product": product,
                            "main_image": ProductImage.objects.filter(
                                product=product
                            ).first(),
                        }
                        for product in subcategory.product_set.all()[:2]
                    ],
                }
                for subcategory in ProductSubCategory.objects.filter(
                    category=product.category
                )
                if subcategory.product_set.count() > 1
            ],
        }
        # advertized products
        context["adverts"]  = {
            "context_name" : "adverts",
            "results": [
                {
                    "product": advert.product,
                    "supplier": advert.product.store.all().first().supplier,
                    "main_image": ProductImage.objects.filter(product=advert.product).first(),
                }
                for advert in (lambda adverts: random.sample(adverts, len(adverts)))(list(ManagerModels.Advert.active.filter(product__in = showroom_products))[:3])
            ],
        }

        context["new_arrivals"] = {
            "context_name": "new-arrivals",
            "results": [
                {
                    "product": product,
                    "main_image": ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in Product.objects.filter(store__in=showroom.store.all()).order_by("-id")[:12]
            ],
        }

        return context


class ServiceListView(ListView):
    model = ManagerModels.Service

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["view_name"] = _("Services")
        return context


class AboutUsView(TemplateView):
    template_name = "manager/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["view_name"] = _("About Us")
        return context


def profile(request):
    if not request.user.is_authenticated:
        return redirect(
            "{}?next={}".format(reverse("auth_app:login"), request.GET.get("next"))
        )

    if request.user.account_type == "SUPPLIER":
        # to supplier profile
        return redirect(reverse("supplier:profile"))
    elif request.user.account_type == "BUYER":
        # to buyer profile
        return redirect(reverse("buyer:profile"))
    elif request.user.account_type == "SUPPORT":
        return redirect(reverse("app_admin:profile"))
    elif request.user.is_superuser:
        return redirect(reverse("app_admin:profile"))


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect(
            "{}?next={}".format(reverse("auth_app:login"), request.GET.get("next"))
        )

    if request.user.account_type == "SUPPLIER":
        # to supplier dashboard
        return redirect(reverse("supplier:dashboard"))
    elif request.user.account_type == "BUYER":
        # to buyer dashboard
        return redirect(reverse("buyer:dashboard"))
    elif request.user.account_type == "SUPPORT":
        return redirect(reverse("app_admin:home"))
    elif request.user.is_superuser:
        return redirect(reverse("app_admin:home"))


class SupportView(View):
    template_name = "manager/support.html"

    def get(self, request):

        context_data = {
            "view_name": _("Support"),
            "discussions": ManagerModels.Discussion.objects.all().order_by("-id")[:10],
        }

        return render(request, self.template_name, context=context_data)


class SupportChatroomView(AuthedOnlyAccessMixin, View):
    template_name = "manager/chatroom.html"

    def get(self, request):
        if request.user.account_type.lower() in ["support", "admin"]:
            return redirect(reverse("app_admin:home"))

        if not request.COOKIES.get("chatroom_roomname", None):
            room_name = str(uuid.uuid4()).replace("-", "")
            context_data = {"view_name": _("Support"), "room_name": room_name}
            response = render(request, self.template_name, context=context_data)
            response.set_cookie("chatroom_roomname", value=room_name, max_age=86400)
        else:
            room_name = request.COOKIES.get("chatroom_roomname", None)
            context_data = {"view_name": _("Support"), "room_name": room_name}
            response = render(request, self.template_name, context=context_data)

        return response


class SupportDiscussionListView(View):
    model = ManagerModels.Discussion
    template_name = "manager/discussion_list.html"

    def get(self, request):

        context_data = {
            "view_name": _("Discussion"),
            "discussions": ManagerModels.Discussion.objects.filter(
                Q(subject__icontains=self.request.GET.get("search", None))
                | Q(description__icontains=self.request.GET.get("search", None))
            ),
        }

        return render(request, self.template_name, context=context_data)


class SupportCreateDiscussionView(AuthedOnlyAccessMixin, View):
    template_name = "manager/create_discussion.html"

    def get(self, request):
        context_data = {"view_name": _("Support")}
        return render(request, self.template_name, context=context_data)

    def post(self, request):
        subject = request.POST.get("subject")
        description = request.POST.get("description")

        discussion = ManagerModels.Discussion.objects.create(
            subject=subject, description=description, user=request.user
        )

        if not discussion:
            messages.add_message(
                request, messages.ERROR, _("Error occurred. Try Again")
            )
            return redirect(reverse("manager:create-discussion"))

        fields = ("subject", "description")
        instance = discussion
        modal = ManagerModels.Discussion

        # ManagerTasks.make_manager_model_translations.delay(fields, instance.pk, instance.__class__.__name__)

        messages.add_message(
            request, messages.SUCCESS, _("Discussion created successfully.")
        )
        return redirect(reverse("manager:create-discussion"))


class SupportDiscussionView(View):
    template_name = "manager/discussion.html"

    def get(self, request, slug):
        discussion = ManagerModels.Discussion.objects.filter(slug=slug).first()
        context_data = {
            "view_name": _("Support"),
            "discussion": discussion,
            "replies": ManagerModels.DiscussionReply.objects.filter(
                discussion=discussion
            ),
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, slug):
        description = request.POST.get("description")
        discussion = ManagerModels.Discussion.objects.filter(slug=slug).first()

        discussion_reply = ManagerModels.DiscussionReply.objects.create(
            description=description, user=request.user, discussion=discussion
        )

        if not discussion_reply:
            messages.add_message(
                request, messages.ERROR, _("Error occurred. Try Again")
            )
            return redirect(
                reverse("manager:discussion", kwargs={"slug": discussion.slug})
            )

        fields = ("description",)
        instance = discussion_reply
        modal = ManagerModels.DiscussionReply

        # ManagerTasks.make_manager_model_translations.delay(fields, instance.pk, instance.__class__.__name__)

        messages.add_message(
            request, messages.SUCCESS, _("Reply submitted successfully.")
        )
        return redirect(reverse("manager:discussion", kwargs={"slug": discussion.slug}))


def blockDasboardAccess(request):
    return render(request, "utils/blockedAccess.html")

def ProfileNotFound(request):
    return render(request, "utils/profile404.html")


def memberships(request):
    context_data = {"view_name": _("Membership Guide")}
    return render(
        request, template_name="manager/guides/memberships.html", context=context_data
    )


def showrooms(request):
    context_data = {
        "view_name": _("Showrooms Guide"),
        "showrooms": ManagerModels.Showroom.objects.all(),
    }
    return render(
        request, template_name="manager/guides/showrooms.html", context=context_data
    )


def stores(request):
    context_data = {
        "view_name": _("Stores Guide"),
    }
    return render(
        request, template_name="manager/guides/stores.html", context=context_data
    )


def services(request):
    context_data = {
        "view_name": _("Supplier Services Guide"),
    }
    return render(
        request, template_name="manager/guides/services.html", context=context_data
    )


def products(request):
    context_data = {
        "view_name": _("Supplier Products Guide"),
    }
    return render(
        request, template_name="manager/guides/products.html", context=context_data
    )


def accounts(request):
    context_data = {
        "view_name": _("Account Creation Guide"),
    }
    return render(
        request, template_name="manager/guides/accounts.html", context=context_data
    )
