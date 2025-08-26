from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.contrib import messages
from django.db.models import Count

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from django.contrib.sites.shortcuts import get_current_site

import random
import openpyxl
from openpyxl.styles import Font


from supplier import models as SupplierModels
from auth_app import models as AuthModels
from manager import models as ManagerModels
from payment import models as PaymentModels
import supplier

from manager import tasks as ManagerTasks
from coms import models as ComsModels

from supplier.mixins import SupplierOnlyAccessMixin

from django.utils.translation import get_language
from googletrans import Translator
from django.conf import settings

translator = Translator()

from auth_app import forms as AuthForms

from supplier import tasks as SupplierTask
from auth_app import tasks as AuthTask

import pandas as pd
from PIL import Image as PILImage
import io
from django.core.files.uploadedfile import InMemoryUploadedFile


class SupplierDetailView(DetailView):
    model = AuthModels.ClientProfile
    template_name = "supplier/supplier_detail.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        supplier = self.get_object()

        context["view_name"] = supplier.business_name

        context["supplier_service"] = {
            "context_name": "supplier-service",
            "results": [
                {
                    "service" : service,
                    "tags" : SupplierModels.ServiceTag.objects.filter(service=service)
                }
                for service in SupplierModels.Service.objects.filter(supplier=supplier.user)
            ]
        }

        context["products"] = {
            "context-name": "products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": product.productimage_set.all().first(),
                }
                for product in SupplierModels.Product.objects.all()
                if supplier.user in [store.supplier for store in product.store.all()]
            ],
        }
        context["stores"] = {
            "context_name": "stores",
            "results": SupplierModels.Store.objects.filter(Q(supplier=supplier.user))[
                :10
            ],
        }

        return context


class SupplierContactView(View):
    template_name = "supplier/contact_supplier.html"

    def get(self, request, slug):
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))

        context_data = dict()
        context_data["view_name"] = "Contact Supplier"
        context_data["profile"] = AuthModels.ClientProfile.objects.filter(
            slug=slug
        ).first()
        context_data["user_profile"] = AuthModels.ClientProfile.objects.filter(
            user=request.user
        ).first()

        return render(request, self.template_name, context=context_data)

    def post(self, request, slug):
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        user = AuthModels.ClientProfile.objects.filter(slug=slug).first().user

        if not all([subject, message]):
            messages.add_message(
                request,
                messages.ERROR,
                _("Please fill all fields."),
            )
            return redirect(reverse("supplier:supplier-contact", args=[slug]))

        ManagerTasks.send_mail.delay(
            subject = subject,
            content = f'Hello, {user.username}, \n{message}',
            _to = [f"{user.email}"],
            _reply_to = [f"{settings.SUPPORT_EMAIL}"]
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _("Submitted successfully."),
        )
        return redirect(reverse("supplier:supplier-contact", args=[slug]))


class SupplierContractView(View):
    template_name = "supplier/contract.html"

    def get(self, request, slug):
        context_data = dict()
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))
        elif request.user.is_authenticated and not request.user.account_type == "BUYER":
            messages.add_message(
                request,
                messages.ERROR,
                _("Please create a buyer account to create a contract."),
            )
            context_data["is_buyer"] = False
        else:
            context_data["is_buyer"] = True

        service = SupplierModels.Service.objects.filter(slug=slug).first()
        context_data["view_name"] = "Contracts"
        context_data["service"] = service
        context_data["supplier"] = AuthModels.ClientProfile.objects.filter(
            user=service.supplier
        ).first()

        return render(request, self.template_name, context=context_data)

    def post(self, request, slug):

        service = SupplierModels.Service.objects.filter(slug=slug).first()
        if not request.user.is_authenticated:
            return redirect(reverse("auth_app:login"))
        elif request.user.is_authenticated and not request.user.account_type == "BUYER":
            messages.add_message(
                request,
                messages.ERROR,
                _("Please create a buyer account to create a contract."),
            )
            return redirect(reverse("supplier:supplier-contract", args=[service.slug]))

        contract_start_date = request.POST.get("contract-start-date")
        contract_end_date = request.POST.get("contract-end-date")

        supplier = AuthModels.Supplier.objects.filter(
            username=service.supplier.username
        ).first()
        buyer = AuthModels.Supplier.objects.filter(
            username=request.user.username
        ).first()

        PaymentModels.Contract.objects.create(
            supplier=supplier,
            buyer=buyer,
            service=service,
            start_date=contract_start_date,
            end_date=contract_end_date,
        )

        # send email to supplier

        ManagerTasks.send_mail.delay(
            subject = _("Foroden Contract Created"),
            content = _(f"Hello, {supplier.username}.\nA Contract application has been sumbited by {buyer.profile.business_name} on service {service.name}.\nPlease visit the dashboard to respond to the application.\nThank you."),
            _to = [f"{supplier.email}"],
            _reply_to = [f"{settings.SUPPORT_EMAIL}"]
        )
        email.send(fail_silently=False)

        return redirect(reverse("buyer:contracts"))


class ProductListView(View):
    model = SupplierModels.ProductSubCategory
    template_name = "supplier/product_list.html"
    PER_PAGE_COUNT = 20

    def get(self, request):

        return render(
            request, template_name=self.template_name, context=self.get_context_data()
        )

    def get_queryset(self):

        # get query parameters
        min_price = self.request.GET.get("min-price", 0)
        max_price = self.request.GET.get("max-price", None)
        supplier = self.request.GET.get("supplier", "all")
        country = self.request.GET.get("country", "all")
        category = self.request.GET.get("category", "all")
        search = self.request.GET.get("search", None)

        if max_price and supplier != "All":
            return SupplierModels.Product.objects.filter(
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(price__lte=float(max_price)),
                Q(business__business_name=supplier)
            )

        elif max_price:
            return SupplierModels.Product.objects.filter(
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(price__lte=float(max_price)),
            )

        elif supplier != "all":
            return SupplierModels.Product.objects.filter(
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(business__business_name=supplier),
            )

        elif country != "all":
            return SupplierModels.Product.objects.filter(
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(business__country=country)
            )

        elif category != "all":
            return SupplierModels.Product.objects.filter(
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(category__name=category),
            )

        elif search:
            # we are searching for products based on name, sub category, category, tag
            return SupplierModels.Product.objects.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(sub_category__name__icontains=search)
                | Q(category__name__icontains=search)
                | Q(productcolor__name__icontains=search)
                | Q(productmaterial__name__icontains=search)
                | Q(producttag__name__icontains=search)
                | Q(business__business_name__icontains=search)
                | Q(business__country__icontains=search)
                | Q(business__city__icontains=search)
            ).distinct("id")

        return SupplierModels.Product.objects.filter(
            price__gte=float(min_price) if min_price else float(0)
        )

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

        context_data["new_arrivals"] = {
            "context_name": "new_arrivals",
            "results": [
                {
                    "product": product,
                    "main_image": SupplierModels.ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in (
                    lambda products: random.sample(products, len(products))
                )(list(SupplierModels.Product.objects.all().order_by("-id")[:10]))
            ],
        }

        context_data["suppliers"] = {
            "context_name": "suppliers",
            "results": AuthModels.Supplier.supplier.all().distinct(),
        }
        context_data["countries"] = {
            "context_name": "countries",
            "results": AuthModels.ClientProfile.objects.all().distinct().only("country")
        }
        context_data["categories"] = {
            "context_name": "categories",
            "results": SupplierModels.ProductCategory.objects.all().distinct().only("name")
        }

        context_data["price_limits"] = {
            "context_name": "price-limits",
            "results": {
                "min_price": self.request.GET.get("min-price", 0),
                "max_price": self.request.GET.get("max-price", None),
            },
        }
        return context_data


class ProductDetailView(DetailView):
    model = SupplierModels.Product

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        response = render(request, self.get_template_names(), context=context)

        if request.COOKIES.get("user_categories", None):
            user_categories = (
                str(self.object.category.id)
                + ","
                + request.COOKIES.get("user_categories")
            )
        else:
            user_categories = str(self.object.category.id)

        response.set_cookie("user_categories", value=user_categories)

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        if self.request.COOKIES.get("user_categories", None):
            user_categories = [
                int(id) for id in self.request.COOKIES.get("user_categories").split(",")
            ]
        else:
            user_categories = []

        context["user_categories"] = {
            "context_name": "user categories",
            "results": SupplierModels.ProductCategory.objects.filter(
                id__in=user_categories
            )[:4],
        }

        context["view_name"] = product.name
        context["product_supplier"] = {
            "context_name": "product-supplier",
            "results": product.store.all().first().supplier,
        }
        context["product_stores"] = {
            "context_name": "product-stores",
            "results": product.store.all(),
        }
        context["product_images"] = {
            "context_name": "product-images",
            "results": SupplierModels.ProductImage.objects.filter(product=product),
        }
        context["product_videos"] = {
            "context_name": "product-videos",
            "results": SupplierModels.ProductVideo.objects.filter(product=product),
        }
        context["tags"] = SupplierModels.ProductTag.objects.filter(product=product)
        context["colors"] = SupplierModels.ProductColor.objects.filter(product=product)
        context["materials"] = SupplierModels.ProductMaterial.objects.filter(product=product)
        context["pricings"] = SupplierModels.ProductPrice.objects.filter(product=product)
        context["products"] = {
            "context_name": "related-products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": SupplierModels.ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in (
                    lambda products: random.sample(products, len(products))
                )(
                    list(
                        SupplierModels.Product.objects.filter(
                            ~Q(id=product.id),
                            Q(sub_category=product.sub_category)
                            | Q(category=product.category),
                        )[:10]
                    )
                )
            ],
        }


        text_promotion = ManagerModels.Promotion.objects.filter(has_image=False)

        context["text_promotion"] = {
            "context_name": "text_promotion",
            "results": (
                    lambda ads: random.sample(ads, len(ads))
                )(list(text_promotion.order_by("-id")[:5]))[1] if text_promotion else None
        }

        context["new_arrivals"] = {
            "context_name": "new-arrivals",
            "results": [
                {
                    "product": product,
                    "main_image": SupplierModels.ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in (
                    lambda products: random.sample(products, len(products))
                )(list(SupplierModels.Product.objects.all().order_by("-id")[:10]))
            ],
        }

        context["advertised_products"] = {
            "context_name": "advertised_products",
            "results": [
                {
                    "product": advert.product,
                    "main_image": SupplierModels.ProductImage.objects.filter(product=advert.product).first(),
                }
                for advert in (lambda adverts: random.sample(adverts, len(adverts)))(list(ManagerModels.Advert.active.all())[:3])
            ],
        }

        context["category_group"] = {
            "context_name": "product-category-group",
            "category": product.category,
            "results": [
                {
                    "subcategory": subcategory,
                    "results": [
                        {
                            "product": product,
                            "main_image": SupplierModels.ProductImage.objects.filter(
                                product=product
                            ).first(),
                        }
                        for product in subcategory.product_set.all()[:2]
                    ],
                }
                for subcategory in SupplierModels.ProductSubCategory.objects.filter(
                    category=product.category
                )
                if subcategory.product_set.count() > 1
            ],
        }
        return context


class NewArrivalView(View):
    template_name = "supplier/promotions.html"

    def get(self, request):

        return render(request, self.template_name, context=self.get_context_data())

    def get_queryset(self, showroom=None):
        if showroom:
            return SupplierModels.Product.objects.filter(store__in=showroom.store.all())
        return SupplierModels.Product.objects.all().order_by("-id")

    def get_products_paginator(self, showroom=None):

        PER_PAGE_COUNT = 20

        self.subcategory_products = self.get_queryset(showroom)

        paginator = Paginator(self.subcategory_products.order_by("-id"), PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):

        showroom = self.request.GET.get("showroom", None)
        if showroom:
            showroom = ManagerModels.Showroom.objects.filter(slug=showroom).first()
            
        context_data = dict()

        products_paginator = self.get_products_paginator(showroom=showroom)
        context_data = dict()

        context_data["view_name"] = "Promotions"
        context_data["page_obj"] = products_paginator
        context_data["product_count"] = self.subcategory_products.count()
        context_data["current_page_number"] = self.request.GET.get("page", 1)

        context_data["products"] = {
            "context_name": "new_arrivals",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": product.productimage_set.all().first(),
                }
                for product in products_paginator.object_list
            ],
        }

        # preview_products only shows Advertised products
        context_data["preview_products"] = {
            "context_name": "preview_products",
            "results": [
                {
                    "product": advert.product,
                    "supplier": advert.product.store.all().first().supplier,
                    "main_image": SupplierModels.ProductImage.objects.filter(product=advert.product).first(),
                }
                for advert in (lambda adverts: random.sample(adverts, len(adverts)))(list(ManagerModels.Advert.active.filter(product__in = SupplierModels.Product.objects.filter(store__in=showroom.store.all())))[:12])
            ]
            if showroom else
            [
                {
                    "product": advert.product,
                    "supplier": advert.product.store.all().first().supplier,
                    "main_image": SupplierModels.ProductImage.objects.filter(product=advert.product).first(),
                }
                for advert in (lambda adverts: random.sample(adverts, len(adverts)))(list(ManagerModels.Advert.active.all())[:12])
            ],
        }

        
        context_data["stores"] = {
            "context_name": "stores",
            "results": showroom.store.all() if showroom else SupplierModels.Store.objects.all().order_by("-id")[:6]
        }

        return context_data


# advertising
class SuperDealsView(View):
    template_name = "supplier/deals.html"

    def get(self, request):

        return render(request, self.template_name, context=self.get_context_data())

    def get_queryset(self):
        return SupplierModels.Product.objects.all().order_by("-id")

    def get_products_paginator(self):

        PER_PAGE_COUNT = 20

        self.subcategory_products = self.get_queryset()

        paginator = Paginator(self.subcategory_products.order_by("-id"), PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):
        context_data = dict()

        products_paginator = self.get_products_paginator()
        context_data = dict()

        context_data["view_name"] = "Promotions"
        context_data["page_obj"] = products_paginator
        context_data["product_count"] = self.subcategory_products.count()
        context_data["current_page_number"] = self.request.GET.get("page", 1)

        context_data["products"] = {
            "context_name": "new_arrivals",
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


class CategoryListView(ListView):
    model = SupplierModels.ProductCategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        categories = self.get_queryset()

        context["view_name"] = _("Categories")

        object_list = []
        for category in categories:
            category_group = {
                "category": category,
                "sub_categories": SupplierModels.ProductSubCategory.objects.filter(
                    category=category
                ),
            }
            object_list.append(category_group)

        context["context_name"] = "product-categories"
        context["object_list"] = object_list

        return context


class CategoryDetailView(DetailView):
    model = SupplierModels.ProductCategory

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        context["view_name"] = category.name

        # products = []
        # for sub_category in SupplierModels.ProductSubCategory.objects.filter(
        #     category=category
        # ):
        #     if not sub_category.product_set.count() < 1:
        #         sub_category_group = {
        #             "sub_category": sub_category.name,
        #             "count": sub_category.product_set.count(),
        #             "results": {
        #                 "products": [
        #                     {
        #                         "product": product,
        #                         "image": SupplierModels.ProductImage.objects.filter(
        #                             product=product
        #                         ).first(),
        #                     }
        #                     for product in sub_category.product_set.all()
        #                 ]
        #             },
        #         }
        #         products.append(sub_category_group)

        context["products"] = {
            "context_name": "products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": SupplierModels.ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in SupplierModels.Product.objects.filter(
                    sub_category__in=SupplierModels.ProductSubCategory.objects.filter(
                        category=category
                    )
                )
            ],
        }

        context["sub_categories"] = {
            "context_name": "sub-catogeries",
            "results": SupplierModels.ProductSubCategory.objects.filter(
                category=category
            ),
        }

        context["product_count"] = {
            "context_name": "product-count",
            "results": category.product_count,
        }
        context["other_categories"] = {
            "context_name": "other-categories",
            "results": SupplierModels.ProductCategory.objects.all()[:20],
        }

        return context


class SubCategoryDetailView(View):
    model = SupplierModels.ProductSubCategory
    template_name = "supplier/products.html"

    def get(self, request, category_slug, sub_category_slug):

        return render(
            request,
            template_name=self.template_name,
            context=self.get_context_data(
                category_slug=category_slug, sub_category_slug=sub_category_slug
            ),
        )

    def get_queryset(self, subcategory):

        # get query parameters
        min_price = self.request.GET.get("min-price", 0)
        max_price = self.request.GET.get("max-price", None)
        price = self.request.GET.get("price", None)
        supplier = self.request.GET.get("supplier", "all")
        country = self.request.GET.get("country", "all")
        showroom = self.request.GET.get("showroom", None)

        if max_price and supplier != "All":
            return SupplierModels.Product.objects.filter(
                Q(sub_category=subcategory),
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(price__lte=float(max_price)),
                Q(business__business_name=supplier),
            )

        elif price:
            return SupplierModels.Product.objects.filter(price=float(price))

        elif max_price:
            return SupplierModels.Product.objects.filter(
                Q(sub_category=subcategory),
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(price__lte=float(max_price)),
            )

        elif supplier != "all":
            return SupplierModels.Product.objects.filter(
                Q(sub_category=subcategory),
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(business__business_name=supplier),
            )

        elif country != "all":
            return SupplierModels.Product.objects.filter(
                Q(sub_category=subcategory),
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(business__country=country),
            )

        elif showroom:
            return SupplierModels.Product.objects.filter(
                Q(sub_category=subcategory),
                Q(price__gte=float(min_price) if min_price else float(0)),
                Q(business__business_name=supplier),
            )

        return SupplierModels.Product.objects.filter(
            Q(sub_category=subcategory),
            Q(price__gte=float(min_price) if min_price else float(0)),
        )

    def get_products_paginator(self, subcategory):

        PER_PAGE_COUNT = 20

        self.subcategory_products = self.get_queryset(subcategory)

        paginator = Paginator(self.subcategory_products.order_by("-id"), PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):
        context_data = dict()

        self.subcategory = self.model.objects.filter(
            slug=kwargs.get("sub_category_slug")
        ).first()

        products_paginator = self.get_products_paginator(self.subcategory)

        context_data["view_name"] = self.subcategory.name
        context_data["page_obj"] = products_paginator
        context_data["product_count"] = self.subcategory_products.count()
        context_data["current_page_number"] = self.request.GET.get("page", 1)

        context_data["subcategory_data"] = {
            "context-name": "subcategory-data",
            "results": {
                "category": self.subcategory.category,
                "sub_category": self.subcategory,
                "count": self.subcategory.product_set.count(),
            },
        }

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

        context_data["new_arrivals"] = {
            "context_name": "new_arrivals",
            "results": [
                {
                    "product": product,
                    "main_image": SupplierModels.ProductImage.objects.filter(
                        product=product
                    ).first(),
                }
                for product in SupplierModels.Product.objects.all().order_by("-id")[:6]
            ],
        }

        context_data["related_subcategories"] = {
            "context_name": "related-subcategories",
            "results": [
                {
                    "subcategory": subcategory,
                    "products": [
                        {
                            "product": product,
                            "main_image": SupplierModels.ProductImage.objects.filter(
                                product=product
                            ).first(),
                        }
                        for product in subcategory.product_set.all()[:4]
                    ],
                }
                for subcategory in self.model.objects.filter(
                    Q(category=self.subcategory.category), ~Q(id=self.subcategory.id)
                )
                if subcategory.product_set.count() > 3
            ],
        }

        context_data["stores"] = {
            "context_name": "stores",
            "results": [
                {
                    "store": store,
                    "products": [
                        {
                            "product": product,
                            "main_image": SupplierModels.ProductImage.objects.filter(
                                product=product
                            ).first(),
                        }
                        for product in SupplierModels.Product.objects.all()
                        if store in product.store.all()
                    ][:3],
                }
                for store in SupplierModels.Store.objects.all()[:4]
                if store.store_product.count() > 0
            ],
        }

        context_data["suppliers"] = {
            "context_name": "suppliers",
            "results": AuthModels.Supplier.supplier.all().distinct(),
        }
        context_data["countries"] = {
            "context_name": "countries",
            "results": AuthModels.ClientProfile.objects.all().distinct().only("country")
        }

        context_data["price_limits"] = {
            "context_name": "price-limits",
            "results": {
                "min_price": self.request.GET.get("min-price", 0),
                "max_price": self.request.GET.get("max-price", None),
            },
        }

        return context_data


class StoreDetailView(DetailView):
    model = SupplierModels.Store

    def get_products_paginator(self):

        PER_PAGE_COUNT = 20

        self.store_products = self.get_object().store_product.all()

        paginator = Paginator(self.store_products.order_by("-id"), PER_PAGE_COUNT)

        page_num = self.request.GET.get("page", 1)
        return paginator.page(page_num)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        store = self.get_object()

        products_paginator = self.get_products_paginator()

        context["page_obj"] = products_paginator
        context["current_page_number"] = self.request.GET.get("page", 1)

        context["view_name"] = store.name
        context["showrooms"] = {
            "context_name": "showrooms",
            "results": ManagerModels.Showroom.objects.filter(store=store),
        }
        context["products"] = {
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
        context["product_count"] = {
            "context_name": "product-count",
            "results": store.store_product.count(),
        }
        context["suppiler_stores"] = {
            "context_name": "suppiler_stores",
            "results": SupplierModels.Store.objects.filter(
                Q(supplier=store.supplier), ~Q(id=store.id)
            ).order_by("-id")[:6],
        }
        context["showroom_stores"] = {
            "context_name": "showroom_stores",
            "results": [
                showroom.store.all()
                for showroom in ManagerModels.Showroom.objects.filter(store=store)
            ]
        }
        return context


class StoreListView(ListView):
    model = SupplierModels.Store
    paginate_by = 20

    def get_queryset(self):
        supplier_filter_param = self.request.GET.get("supplier", None)
        if supplier_filter_param:
            supplier = (
                AuthModels.ClientProfile.objects.filter(
                    business_name=supplier_filter_param
                )
                .first()
                .user
            )
            return self.model.objects.filter(supplier=supplier).order_by("-id")

        return super().get_queryset().order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["view_name"] = _("Stores")

        context["suppliers"] = {
            "context_name": "suppliers",
            "results": AuthModels.Supplier.supplier.all(),
        }

        return context


class SearchView(View):
    model = SupplierModels.Product
    template_name = "supplier/product_list.html"
    PER_PAGE_COUNT = 20

    def get(self, request):

        return render(
            request, template_name=self.template_name, context=self.get_context_data()
        )

    def get_queryset(self):
        # context['str']
        pass


# dashboard
class DashboardView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/dashboard.html"

    def get(self, request):
        return render(request, self.template_name, self.get_context_data())

    def get_context_data(self, **kwargs):
        context_data = dict()

        context_data["view_name"] = _("Supplier Dashboard")
        context_data["active_tab"] = "Dashboard"
        context_data["statistics"] = {
            "context_name": "statistics",
            "results": [
                {
                    "name": _("Stores"),
                    "count": SupplierModels.Store.objects.filter(
                        supplier=self.request.user
                    ).count(),
                },
                {
                    "name": _("Products"),
                    "count": SupplierModels.Product.objects.filter(
                        store__in=SupplierModels.Store.objects.filter(
                            supplier=self.request.user
                        )
                    ).count(),
                },
                {
                    "name": _("Services"),
                    "count": SupplierModels.Service.objects.filter(
                        supplier=self.request.user
                    ).count(),
                },
                {
                    "name": _("Contracts"),
                    "count": PaymentModels.Contract.objects.filter(
                        supplier=self.request.user
                    ).count(),
                },
            ],
        }

        context_data["category_group"] = [
            obj
            for obj in SupplierModels.Product.objects.filter(store__supplier=self.request.user).values("category__name")
            .annotate(dcount=Count("category"))
            .order_by()
        ]

        context_data["latest_products"] = {
            "context_name": "latest-products",
            "results": SupplierModels.Product.objects.filter(store__supplier=self.request.user).order_by("-id")[:4],
        }
        context_data["orders"] = [
            obj
            for obj in SupplierModels.Order.objects.filter(supplier=self.request.user.business)
            .values("status")
            .annotate(dcount=Count("status"))
            .order_by()
        ]
        return context_data


class ProfileView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/profile.html"

    def get(self, request):
        context_data = {
            "profile": AuthModels.ClientProfile.objects.filter(
                user=request.user
            ).first(),
            "memberships": [
                {
                    "membership": membership,
                    "plan_group": membership.feature.features_list.first().group,
                } for membership in PaymentModels.Membership.active.filter(client=request.user).order_by("-id")
            ]
        }
        return render(request, self.template_name, context=context_data)

class BusinessProfileView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/business_profile.html"

    def get(self, request):
        context_data = {
            "profile": AuthModels.ClientProfile.objects.filter(
                user=request.user
            ).first()
        }
        return render(request, self.template_name, context=context_data)


def password_reset(request):
    if request.method == "GET":
        return render(request, "supplier/dashboard/password_reset.html")

    if request.method == "POST":
        if request.POST.get("new_password") != request.POST.get("confirm_new_password"):
            messages.add_message(request, messages.ERROR, _("Password mismatch."))
            return redirect(reverse("supplier:password-reset"))

        # confirm current password
        user = authenticate(
            username=request.user.username,
            password=request.POST.get("current_password"),
        )
        if not user:
            messages.add_message(
                request, messages.ERROR, _("Wrong current password entered.")
            )
            return redirect(reverse("supplier:password-reset"))

        if authenticate(
            username=request.user.username, password=request.POST.get("new_password")
        ):
            messages.add_message(request, messages.ERROR, _("No modification made."))
            return redirect(reverse("supplier:password-reset"))

        # make password
        generated_password = make_password(request.POST.get("new_password"))
        user = AuthModels.User.objects.filter(pk=request.user.pk).first()
        user.password = generated_password
        user.save()
        messages.add_message(
            request, messages.SUCCESS, _("Account password reset successfully")
        )
        return redirect(reverse("supplier:profile"))


class EditAccountsProfileView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/account_edit.html"

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
            return redirect(reverse("supplier:dashboard-editaccountsprofile"))

        if (
            request.POST.get("first_name") == request.user.first_name
            and request.POST.get("last_name") == request.user.last_name
            and request.POST.get("username") == request.user.username
            and request.POST.get("email") == request.user.email
        ):
            messages.add_message(
                request, messages.ERROR, _("No modification was made.")
            )
            return redirect(reverse("supplier:dashboard-editaccountsprofile"))

        if (
            AuthModels.User.objects.filter(username=request.POST.get("username"))
            and request.POST.get("username") != request.user.username
        ):
            messages.add_message(request, messages.ERROR, _("Username not available."))
            return redirect(reverse("supplier:dashboard-editaccountsprofile"))

        if (
            AuthModels.User.objects.filter(email=request.POST.get("email"))
            and request.POST.get("email") != request.user.email
        ):
            messages.add_message(request, messages.ERROR, _("Email not available."))
            return redirect(reverse("supplier:dashboard-editaccountsprofile"))

        form = AuthForms.UserUpdateFormManager(data=request.POST, instance=request.user)
        if not form.is_valid():
            messages.add_message(request, messages.ERROR, _("Invalid data. Try again."))
            return redirect(reverse("buyer:dashboard-editaccountsprofile"))
        form.save()

        fields = ("first_name", "last_name")
        instance = request.user
        AuthTask.make_user_translations.delay(fields, instance.pk)

        messages.add_message(
            request, messages.SUCCESS, _("Account Details Editted Successfully")
        )
        return redirect(reverse("supplier:profile"))


class EditBusinessProfileView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/business_edit.html"

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
            return redirect(
                reverse("supplier:dashboard-editbusinessprofile", args=[slug])
            )

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
            AuthTask.make_business_translations.delay(fields, instance.pk)

            messages.add_message(
                request, messages.SUCCESS, _("Business Details Editted Successfully.")
            )
            return redirect(reverse("supplier:profile"))
        except Exception as e:
            print(e)
            messages.add_message(
                request, messages.ERROR, _("An Error Occurred. Try Again.")
            )
            return redirect(
                reverse("supplier:dashboard-editbusinessprofile", args=[slug])
            )


class DashboardProductsView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/manage-product.html"

    def get(self, request):
        return render(request, self.template_name)


class DashboardProductsCreateView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/create-product.html"

    def get(self, request):
        context_data = {
            "supplier_profile" : AuthModels.ClientProfile.objects.filter(user=request.user).first(),
            "stores": SupplierModels.Store.objects.filter(supplier=request.user),
            "subcategories": SupplierModels.ProductSubCategory.objects.all(),
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, *args, **kwargs):
        if not (
            request.POST.get("name")
            and request.POST.get("store")
            and request.POST.get("sub_category")
            and request.POST.get("description")
            and request.POST.get("currency")
            and request.POST.get("price")
            and request.FILES.get("images")
        ):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("supplier:dashboard-productscreate"))
        try:
            product = SupplierModels.Product.objects.create(
                name=request.POST.get("name"),
                sub_category=SupplierModels.ProductSubCategory.objects.filter(
                    name=request.POST.get("sub_category")
                ).first(),
                description=request.POST.get("description"),
                currency=request.POST.get("currency"),
                price=request.POST.get("price"),
            )
            store = SupplierModels.Store.objects.filter(
                name=request.POST.get("store")
            ).first()
            product.store.add(store)
            if product:
                for file in request.FILES.getlist("images"):
                    SupplierModels.ProductImage.objects.create(
                        product=product, image=file
                    )

                fields = ("name", "description", "price", "currency")
                instance = product
                modal = SupplierModels.Product
                
                # SupplierTask.make_supplier_model_translations.delay(fields, instance.pk, instance.__class__.__name__)

            messages.add_message(
                request, messages.SUCCESS, _("Product created successfully.")
            )
            return redirect(reverse("supplier:dashboard-productscreate"))
        except Exception as e:
            print(e)
            product.delete()
            messages.add_message(
                request, messages.ERROR, _("An Error occurred. Try Again")
            )
            return redirect(reverse("supplier:dashboard-productscreate"))

class DashboardProductEditView(SupplierOnlyAccessMixin, View):
    def post(self, request, slug):
        product = SupplierModels.Product.admin_list.filter(slug = slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            if request.POST.get('edit_name'):
                product.first().name = request.POST.get("name")
                product.first().save()

            elif request.POST.get('edit_description'):
                product.first().description = request.POST.get("description")
                product.first().save()

            elif request.POST.get('edit_pricing'):
                price = SupplierModels.ProductPrice(
                    product=product.first(),
                    currency=request.POST.get("currency"),
                    min_price=request.POST.get("min-price"),
                    max_price=request.POST.get("max-price"),
                )
                price.save()

            elif request.POST.get('edit_tags'):
                tags = [request.POST.get("tag_1"), request.POST.get("tag_2"), request.POST.get("tag_3")]
                for name in tags:
                    if not name:
                        continue
                    tag = SupplierModels.ProductTag(
                        product=product.first(),
                        name = name
                    )
                    tag.save()

            elif request.POST.get('edit_colors'):
                colors = [request.POST.get("color_1"), request.POST.get("color_2"), request.POST.get("color_3")]
                for name in colors:
                    if not name:
                        continue
                    color = SupplierModels.ProductColor(
                        product=product.first(),
                        name = name
                    )
                    color.save()

            elif request.POST.get('edit_materials'):
                materials = [request.POST.get("material_1"), request.POST.get("material_2"), request.POST.get("material_3")]
                for name in materials:
                    if not name:
                        continue
                    material = SupplierModels.ProductMaterial(
                        product=product.first(),
                        name = name
                    )
                    material.save()

            elif request.POST.get('edit_images'):
                files = request.FILES.getlist("images")
                for media in files:
                    pil_image = PILImage.open(media)
                    
                    # Resize the image
                    # resized_image = pil_image.resize((250, 250))
                    
                    # Optimize the image by reducing the file size
                    optimized_image = io.BytesIO()

                    if pil_image.format != 'JPEG':
                        # Convert image to JPEG format
                        pil_image = pil_image.convert('RGB')

                    pil_image.save(optimized_image, format='JPEG', optimize=True)
                    optimized_image.seek(0)
                    uploaded_image = InMemoryUploadedFile(
                        optimized_image,
                        None,
                        media.name,
                        'image/jpeg',
                        optimized_image.getbuffer().nbytes,
                        None
                    )

                    image = SupplierModels.ProductImage(
                        product=product.first(),
                        image=uploaded_image
                    )              
                    image.save()

            elif request.POST.get('edit_videos'):
                files = request.FILES.getlist("videos")
                for media in files:
                    video = SupplierModels.ProductVideo(
                        product=product.first(),
                        video=media
                    )              
                    video.save()


            messages.add_message(request, messages.SUCCESS, _("Product Details Modified Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))

class DashboardProductCustomizationView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/custom-product.html"

    def get(self, request, slug):
        product = SupplierModels.Product.objects.filter(slug=slug)
        if not product:
            return redirect(reverse("supplier:dashboard-productscreate"))
            
        context_data = {
            "product" : product.first()
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, *args, **kwargs):
        pass


class DashboardBulkUploadView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/bulk-upload.html"

    def get(self, request):
        context_data = {
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("bulk_upload_file")
        business = AuthModels.ClientProfile.objects.filter(user=request.user).first()

        try:
            products_saved = 0
            df = pd.read_excel(excel_file)
            
            for index, row in df.iterrows():
                store = SupplierModels.Store.objects.filter(name=row['store'])
                if not store:
                    messages.add_message(request, messages.ERROR, _("Product {} Not Created! No Store Found with Name: {}.".format(row["name"], row["store"])))
                    continue
                
                sub_category = SupplierModels.ProductSubCategory.objects.filter(name=row['sub_category'])
                if not sub_category:
                    messages.add_message(request, messages.ERROR, _("Product {} Not Created! No Sub Category Found with Name: {}.".format(row["name"], row["sub_category"])))
                    continue

                # product creation
                product = SupplierModels.Product(
                    name = row['name'],
                    description = row['description'],
                    discount = row['discount'],
                    stock = row['stock'],
                    sub_category=sub_category.first()
                )

                if not product:
                    messages.add_message(request, messages.ERROR, _("Product {} Not Created!".format(row["name"])))
                    continue

                
                product.business = business
                product.save()
                store.first().store_product.add(product)
                
                # save labels
                tags = str(row["tags"])
                if not tags.split(",")[0]:
                    location = AuthModels.ClientProfile.objects.filter(user=request.user).first().country
                    tag = SupplierModels.ProductTag(name=location, product=product)
                    tag.save()
                else:
                    for tag_name in tags.split(","):
                        tag = SupplierModels.ProductTag(name=tag_name.strip(), product=product)
                        if not tag:
                            messages.add_message(request, messages.ERROR, _("Tag {} not attached to Product {} Not Created!".format(tag_name, row["name"])))
                            continue
                        tag.save()
                    
                colors = str(row["colors"])
                for color_name in colors.split(","):
                    color = SupplierModels.ProductColor(name=color_name.strip(), product=product)
                    if not color:
                        messages.add_message(request, messages.ERROR, _("Color {} not attached to Product {} Not Created!".format(tag_name, row["name"])))
                        continue
                    color.save()
                    
                materials = str(row["materials"])
                for material_name in materials.split(","):
                    material = SupplierModels.ProductMaterial(name=material_name.strip(), product=product)
                    if not material:
                        messages.add_message(request, messages.ERROR, _("material {} not attached to Product {} Not Created!".format(tag_name, row["name"])))
                        continue
                    material.save()
                    
                price_1 = str(row['price_1']).split(",")
                if len(price_1) > 1:
                    pricing_1 = SupplierModels.ProductPrice(product=product, currency=price_1[0], min_price=price_1[1], max_price=price_1[2])
                    pricing_1.save()

                price_2 = str(row['price_2']).split(",")
                if len(price_2) > 1:
                    pricing_2 = SupplierModels.ProductPrice(product=product, currency=price_2[0], min_price=price_2[1], max_price=price_2[2])
                    pricing_2.save()

                price_3 = str(row['price_3']).split(",")
                if len(price_3) > 1:
                    pricing_3 = SupplierModels.ProductPrice(product=product, currency=price_3[0], min_price=price_3[1], max_price=price_3[2])
                    pricing_3.save()

                products_saved += 1
            
            messages.add_message(request, messages.SUCCESS, _("{} Products Created".format(products_saved)))
            return redirect(reverse("supplier:dashboard-bulkupload"))

        except:
            product.delete()
            messages.add_message(request, messages.ERROR, _("Error Occured While Processing Excel File."))
            return redirect(reverse("supplier:dashboard-bulkupload"))



class DashboardProductDeleteView(SupplierOnlyAccessMixin, View):
    def post(self, request, slug):
        product = SupplierModels.Product.admin_list.filter(slug=slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            product.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Product Deleted."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))

class DashboardProductStoreDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.Store
    def post(self, request, product_slug, slug):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.admin_list.filter(slug = slug)
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):

            if record.first() not in product.first().stores:
                messages.add_message(request, messages.ERROR, _("Product not in store {}.".format(record.first().name)))
                return redirect(reverse("supplier:dashboard-products"))

            if len(product.first().stores) == 1:
                messages.add_message(request, messages.ERROR, _("Product not assigned to another store."))
                return redirect(reverse("supplier:dashboard-products"))

            record.first().store_product.remove(product.first())
            
            # set product supplier
            product.first().business = AuthModels.ClientProfile.objects.filter(user=request.user).first()
            product.first().save()

            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductCategoryDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductCategory
    def post(self, request, product_slug, slug):
        return redirect(reverse("supplier:dashboard-products"))
    #     product = SupplierModels.Product.admin_list.filter(slug = product_slug)
    #     if not product:
    #         messages.add_message(request, messages.ERROR, _("Product Not Found."))
    #         return redirect(reverse("supplier:dashboard-products"))
            
    #     record = self.model.objects.filter(slug = slug, product=product.first())
    #     if not record:
    #         messages.add_message(request, messages.ERROR, _("Record Not Found."))
    #         return redirect(reverse("supplier:dashboard-products"))
        
    #     if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
    #         record.first().delete()
    #         messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
    #         return redirect(reverse("supplier:dashboard-products"))
    #     else:
    #         messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
    #         return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductSubCategoryDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductSubCategory
    def post(self, request, product_slug, slug):
        return redirect(reverse("supplier:dashboard-products"))
    #     product = SupplierModels.Product.admin_list.filter(slug = product_slug)
    #     if not product:
    #         messages.add_message(request, messages.ERROR, _("Product Not Found."))
    #         return redirect(reverse("supplier:dashboard-products"))
            
    #     record = self.model.objects.filter(slug = slug, product=product.first())
    #     if not record:
    #         messages.add_message(request, messages.ERROR, _("Record Not Found."))
    #         return redirect(reverse("supplier:dashboard-products"))
        
    #     if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
    #         record.first().delete()
    #         messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
    #         return redirect(reverse("supplier:dashboard-products"))
    #     else:
    #         messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
    #         return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductPricingDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductPrice
    def post(self, request, product_slug, pk):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(pk = pk, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductTagDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductTag
    def post(self, request, product_slug, pk):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(pk = pk, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductColorDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductColor
    def post(self, request, product_slug, pk):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(pk = pk, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductMaterialDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductMaterial
    def post(self, request, product_slug, pk):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(pk = pk, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductImageDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductImage
    def post(self, request, product_slug, slug):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(slug = slug, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            
class DashboardProductVideoDeleteView(SupplierOnlyAccessMixin, View):
    model = SupplierModels.ProductVideo
    def post(self, request, product_slug, slug):
        product = SupplierModels.Product.admin_list.filter(slug = product_slug)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
            
        record = self.model.objects.filter(slug = slug, product=product.first())
        if not record:
            messages.add_message(request, messages.ERROR, _("Record Not Found."))
            return redirect(reverse("supplier:dashboard-products"))
        
        if AuthModels.ClientProfile.objects.filter(user = request.user) and product.first().supplier in AuthModels.ClientProfile.objects.filter(user = request.user):
            record.first().delete()
            messages.add_message(request, messages.SUCCESS, _("Record Deleted Successfully."))
            return redirect(reverse("supplier:dashboard-products"))
        else:
            messages.add_message(request, messages.ERROR, _("Operation Forbidden."))
            return redirect(reverse("supplier:dashboard-products"))
            
            

class DashboardStoresView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/manage-store.html"

    def get(self, request):

        context_data = dict()

        membership = PaymentModels.Membership.active.filter(client=request.user).first()
        if not membership:
            context_data["showrooms"] = None

        elif "One" in membership.feature.name:
            supplier_stores = SupplierModels.Store.objects.filter(supplier=request.user)
            for store in supplier_stores:
                if len(store.store.all()) > 0:
                    context_data["showrooms"] = store.store.all()
                else:
                    context_data["showrooms"] = ManagerModels.Showroom.objects.all()
            
        elif "Showroom" in membership.feature.name:
            context_data["showrooms"] = ManagerModels.Showroom.objects.all()

        context_data["products"] = {
            "context-name": "products",
            "results": [
                {
                    "product": product,
                    "supplier": product.store.all().first().supplier,
                    "images": product.productimage_set.all().first(),
                }
                for product in SupplierModels.Product.objects.all()
                if request.user in [store.supplier for store in product.store.all()]
            ],
        }

        return render(request, self.template_name, context=context_data)


class DashboardStoresCreateView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/create-store.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if not (request.POST.get("name") and request.FILES.get("image")):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("supplier:dashboard-storescreate"))

        name = request.POST.get("name")
        image = request.FILES.get("image")

        if SupplierModels.Store.objects.filter(name=name):
            messages.add_message(
                request, messages.ERROR, _("Please use a different store name.")
            )
            return redirect(reverse("supplier:dashboard-storescreate"))

        try:
            store = SupplierModels.Store.objects.create(
                name=name, image=image, supplier=request.user
            )
            messages.add_message(
                request, messages.SUCCESS, _("Store created successfully.")
            )

            fields = ("name",)
            instance = store
            modal = SupplierModels.Store
            
            # SupplierTask.make_supplier_model_translations.delay(fields, instance.pk, instance.__class__.__name__)

            return redirect(reverse("supplier:dashboard-storescreate"))
        except Exception as err:
            messages.add_message(
                request, messages.ERROR, _("Sorry, an error occurred. Please Try Again")
            )
            return redirect(reverse("supplier:dashboard-storescreate"))


def assign_showroom(request, slug):
    if request.method == "GET":
        return redirect(reverse("supplier:dashboard-stores"))
    if request.method == "POST":
        showroom_name = request.POST.get("showroom")
        try:
            showroom = ManagerModels.Showroom.objects.filter(name=showroom_name).first()
            store = SupplierModels.Store.objects.filter(slug=slug).first()
            showroom.store.add(store)
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Store: {store.name} added to Showroom: {showroom.name}",
            )
            return redirect(reverse("supplier:dashboard-stores"))
        except:
            messages.add_message(
                request, messages.ERROR, _("An Error Occured. Please Try Again")
            )
            return redirect(reverse("supplier:dashboard-stores"))


def add_product(request, slug):
    if request.method == "GET":
        return redirect(reverse("supplier:dashboard-stores"))
    if request.method == "POST":
        product_name = request.POST.get("product")
        try:
            product = SupplierModels.Product.objects.filter(name=product_name).first()
            store = SupplierModels.Store.objects.filter(slug=slug).first()
            store.store_product.add(product)
            messages.add_message(
                request,
                messages.SUCCESS,
                f"Product: {product.name} added to Store: {store.name}",
            )
            return redirect(reverse("supplier:dashboard-stores"))

        except:
            messages.add_message(
                request, messages.ERROR, _("An Error Occured. Please Try Again")
            )
            return redirect(reverse("supplier:dashboard-stores"))


class DashboardContractsView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/contracts.html"

    def get(self, request):
        return render(request, self.template_name)


class DashboardContractsDetailsView(SupplierOnlyAccessMixin, DetailView):
    template_name = "supplier/dashboard/contract-detail.html"
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

    def get_queryset(self):
        return self.model.objects.all()


class DashboardContractRejectDetailsView(SupplierOnlyAccessMixin, View):
    def post(self, request, pk):
        contract = PaymentModels.Contract.objects.filter(pk=pk).first()
        contract.is_accepted = False
        contract.save()
        messages.add_message(request, messages.ERROR, _("Contract has been rejected."))

        ManagerTasks.send_mail.delay(
            subject = _("Foroden Contract Rejected."),
            content = _(f"Hello, {contract.buyer.username}.\nYour contract application on service {contract.service.name} has been rejected.\nPlease contact the supplier for more information.\nThank you."),
            _to = [f"{contract.buyer.email}"],
            _reply_to = [f"{settings.SUPPORT_EMAIL}"]
        )

        return redirect(reverse("supplier:dashboard-contractsdetails", args=[pk]))


class DashboardContractAcceptDetailsView(SupplierOnlyAccessMixin, View):
    def post(self, request, pk):
        contract = PaymentModels.Contract.objects.filter(pk=pk).first()
        contract.is_accepted = True
        contract.save()

        messages.add_message(
            request, messages.SUCCESS, _("Contract has been accepted.")
        )

        domain = get_current_site(request).domain
        link = reverse("payment:contract-payment", kwargs={"pk": contract.pk})
        payment_link = f"http://{domain}{link}"

        ManagerTasks.send_mail.delay(
            subject = _("Foroden Contract Accepted"),
            content = _(f"Hello, {contract.buyer.username}.\nYour contract application on service") + "{contract.service.name}" + _("has been accepted.\nPlease visit the") + "{payment_link}" + _("to complete the application process.\nThank you."),
            _to = [f"{contract.buyer.email}"],
            _reply_to = [f"{settings.SUPPORT_EMAIL}"]
        )

        return redirect(reverse("supplier:dashboard-contractsdetails", args=[pk]))


class DashboardMessengerView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/messenger.html"

    def get(self, request):
        context_data = {
            "business_chat" : ComsModels.InterClientChat.objects.filter(
                Q(initiator=self.request.user.business)
                | Q(participant=self.request.user.business)
            ).first()
        }
        return render(request, self.template_name, context=context_data)

class DashboardNotificationView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/notification.html"

    def get(self, request):
        return render(request, self.template_name)

class DashboardCalendarView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/calendar.html"

    def get(self, request):
        return render(request, self.template_name)

class DashboardServicesView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/services.html"

    def get(self, request):
        return render(request, self.template_name)


class DashboardServicesCreateView(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/create-service.html"

    def get(self, request):
        context_data = {
            "supplier_profile" : AuthModels.ClientProfile.objects.filter(user=request.user).first()
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request, *args, **kwargs):
        if not (
            request.POST.get("name")
            and request.POST.get("description")
            and request.POST.get("currency")
            and request.POST.get("price")
        ):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("supplier:dashboard-servicescreate"))

        name = request.POST.get("name")
        description = request.POST.get("description")
        currency = request.POST.get("currency")
        price = request.POST.get("price")

        if SupplierModels.Service.objects.filter(name=name):
            messages.add_message(
                request, messages.ERROR, _("Please use a different service name.")
            )
            return redirect(reverse("supplier:dashboard-servicescreate"))

        try:
            service = SupplierModels.Service.objects.create(
                name=name,
                description=description,
                currency=currency,
                price=price,
                supplier=request.user,
            )

            fields = ("name", "description", "price", "currency")
            instance = service
            # SupplierTask.make_supplier_model_translations.delay(fields, instance.pk, instance.__class__.__name__)

            # add tags
            for i in range(1, 6):
                tag = request.POST.get(f"tag_{i}", None)
                if not tag:
                    continue

                tag = SupplierModels.ServiceTag.objects.create(
                    name=tag, service=service
                )
                fields = ("name",)
                instance = tag
                # SupplierTask.make_supplier_model_translations.delay(fields, instance.pk, instance.__class__.__name__)


            messages.add_message(
                request, messages.SUCCESS, _("Service created successfully.")
            )

            return redirect(reverse("supplier:dashboard-servicescreate"))
        except:
            messages.add_message(
                request, messages.ERROR, _("Sorry, an error occurred. Please Try Again", err)
            )
            return redirect(reverse("supplier:dashboard-servicescreate"))


class DashboardAdvertiseView(View):
    template_name = 'supplier/dashboard/advertise.html'

    def get(self, request):
        context_data = {
            "products" : SupplierModels.Product.objects.filter(store__supplier=self.request.user).order_by("-id"),
            "advertising_locations" : ManagerModels.AdvertisingLocation.objects.all()
        }
        return render(request, self.template_name, context=context_data)

    def post(self, request):
        product = request.POST.get("product")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        advertising_location = request.POST.get("advertising_location")

        if not all([product, start_date, end_date, advertising_location]):
            messages.add_message(request, messages.ERROR, _("Please Fill all fields."))
            return redirect(reverse("supplier:dashboard-advertise"))

        product = SupplierModels.Product.objects.filter(name=product)
        if not product:
            messages.add_message(request, messages.ERROR, _("Product not found."))
            return redirect(reverse("supplier:dashboard-advertise"))

        date_format = "%m/%d/%Y"
        try:
            datetime.strptime(start_date, date_format)
        except:
            date_format = "%Y-%m-%d"

        location = ManagerModels.AdvertisingLocation.objects.filter(id=advertising_location).first()
        duration = datetime.strptime(end_date, date_format) - datetime.strptime(start_date, date_format)
        price = duration.days * location.price

        advert = ManagerModels.Advert.objects.create(
            product = product.first(),
            location = location,
            start_date = start_date,
            end_date = end_date,
            amount = price
        )

        messages.add_message(
            request,
            messages.SUCCESS,
            _("Submitted successfully. Please make your payment."),
        )
        return redirect(reverse("supplier:dashboard-advertise-payment", args=[advert.slug]))

class DashboardAdvertisePaymentView(View):
    template_name = 'supplier/dashboard/advertise_payment.html'

    def get(self, request, slug):

        advert = ManagerModels.Advert.objects.filter(slug=slug).first()
        context_data = {
            "advert" : advert
        }
        return render(request, self.template_name, context=context_data)


class DashboardPaymentsView(View):
    template_name = 'supplier/dashboard/payment_list.html'

    def get(self, request):

        membershipPayments = PaymentModels.Membership.objects.filter(client = request.user)

        context_data = {
            "memberships" : membershipPayments
        }
        return render(request, self.template_name, context=context_data)


class DashboardAdvertsPaymentsView(View):
    template_name = 'supplier/dashboard/advert_payment_list.html'

    def get(self, request):
        supplier_products = SupplierModels.Product.objects.filter(
            store__in=SupplierModels.Store.objects.filter(supplier=self.request.user)
        )
        context_data = {
            "adverts" : ManagerModels.Advert.active.filter(product__in = supplier_products)
        }
        return render(request, self.template_name, context=context_data)


# orders
class DashboardOrderList(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/orders/order_list.html"
    model = SupplierModels.Order
    PER_PAGE_COUNT = 20

    def get(self, request):

        return render(
            request, template_name=self.template_name, context=self.get_context_data()
        )

    def get_queryset(self):
        # filters => creation date, delivery date, overdue, new, buyer
        self.queryset = self.model.objects.filter(supplier = self.request.user.business)

        buyer_slug = self.request.GET.get("buyer", 0)
        country_name = self.request.GET.get("country", 0)
        if buyer_slug:
            buyer = get_object_or_404(AuthModels.ClientProfile, slug=buyer_slug)
            self.queryset = self.queryset.filter(buyer = buyer)
            
        if self.request.GET.get("overdue", 0):
            today = timezone.now().date()
            self.queryset = self.queryset.filter(delivery_date__lt=today)

        if country_name:
            self.queryset = self.queryset.filter(buyer__country=country_name)
            
        if self.request.GET.get("status", 0):
            if self.request.GET.get("status", 0) != "ALL":
                self.queryset = self.queryset.filter(status=self.request.GET.get("status", 0))

        if self.request.GET.get("order_search_value", 0):
            order_search_value = self.request.GET.get("order_search_value", 0)
            self.queryset = self.queryset.filter(Q(order_id=order_search_value) | Q(buyer__business_name__icontains=order_search_value))

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

        context_data["buyers"] = {
            "context_name": "buyers",
            "results": [order.buyer for order in self.model.objects.filter(supplier = self.request.user.business)]
        }
        context_data["countries"] = {
            "context_name": "countries",
            "results": [order.buyer.country for order in self.model.objects.filter(supplier = self.request.user.business)]
        }
        context_data["statuses"] = {
            "context_name": "statuses",
            "results": [status[0] for status in SupplierModels.Order.order_statuses]
        }
        
        return context_data



class DashboardOrderDetail(SupplierOnlyAccessMixin, View):
    template_name = "supplier/dashboard/orders/order_details.html"
    model = SupplierModels.Order

    def get(self, request, order_id):
        order = get_object_or_404(self.model, order_id=order_id)

        if order.supplier.user != request.user:
            return redirect(reverse("supplier:dashboard-order-list"))

        if order.status == "PENDING":
            order.status = "VIEWED BY SUPPLER"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "VIEWED")

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

        if order.supplier.user != request.user:
            return redirect(reverse("supplier:dashboard-order-list"))

        # # set delivery date
        # print("\n"*3)
        # print("order_notes:", request.POST.get("order_notes"))
        # print("\n"*3)

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
            SupplierTask.notify_buyer.delay(order.order_id, "DELIVERY_DATE_SET")
        
        if request.POST.get("currency") and request.POST.get("agreed_price"):
            currency = request.POST.get("currency")
            agreed_price = float(request.POST.get("agreed_price"))
            order.currency = currency
            order.agreed_price = agreed_price
            order.save()
            BuyerTasks.notify_buyer.delay(order.order_id, "AGREED_PRICE_SET")

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
            

        if request.POST.get("CANCELLED"):
            order.status = "CANCELLED"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "CANCELLED")

        if request.POST.get("ACCEPTED"):
            order.status = "ACCEPTED BY SUPPLER"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "ACCEPTED BY SUPPLIER")

        if request.POST.get("REJECTED"):
            order.status = "REJECTED"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "REJECTED")

        if request.POST.get("IN_DELIVERY"):
            order.status = "IN DELIVERY"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "IN DELIVERY")

            for prod in SupplierModels.OrderProductVariation.objects.filter(order=order):
                prod.product.sell_made(prod.quantity)

        if request.POST.get("DELIVERED"):
            order.status = "DELIVERY"
            order.save()    
            SupplierTask.notify_buyer.delay(order.order_id, "DELIVERED")

        if request.POST.get("COMPLETED"):
            order.status = "COMPLETED"
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "COMPLETED")

        if request.POST.get("REORDER"):
            order.status = "PENDING"
            over.delivery_date = None
            order.save()
            SupplierTask.notify_buyer.delay(order.order_id, "REORDER")

        return redirect(reverse("supplier:dashboard-order-details", kwargs={"order_id": order.order_id}))

def download_excel(request, order_id):
    order = get_object_or_404(SupplierModels.Order, order_id=order_id)
    shipping = get_object_or_404(SupplierModels.OrderShippingDetail, order=order)
    # Create a new workbook and get the active sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # order details
    sheet['A1'] = _('Order Id')
    sheet['A1'].font = Font(bold=True)
    sheet['A2'] = order_id

    sheet['B1'] = _('Supplier')
    sheet['B1'].font = Font(bold=True)
    sheet['B2'] = order.supplier.business_name

    sheet['C1'] = _('Buyer')
    sheet['C1'].font = Font(bold=True)
    sheet['C2'] = order.buyer.business_name

    sheet['D1'] = _('Delivery Date')
    sheet['D1'].font = Font(bold=True)
    sheet['D2'] = order.delivery_date

    sheet['E1'] = _('Agreed Price')
    sheet['E1'].font = Font(bold=True)
    sheet['E2'] = order.agreed_price

    sheet['F1'] = _('Discount')
    sheet['F1'].font = Font(bold=True)
    sheet['F2'] = order.discount

    sheet['G1'] = _('Total Price')
    sheet['G1'].font = Font(bold=True)
    sheet['G2'] = order.total_price

    sheet['H1'] = _('Status')
    sheet['H1'].font = Font(bold=True)
    sheet['H2'] = order.status

    # shipping
    sheet['A4'] = _('Carrier')
    sheet['A4'].font = Font(bold=True)
    sheet['A5'] = shipping.carrier.name
    
    sheet['B4'] = _('Shipping Tax')
    sheet['B4'].font = Font(bold=True)
    sheet['B5'] = shipping.carrier.tax
    
    sheet['C4'] = _('Address 1')
    sheet['C4'].font = Font(bold=True)
    sheet['C5'] = shipping.address_1
    
    sheet['D4'] = _('Address 2')
    sheet['D4'].font = Font(bold=True)
    sheet['D5'] = shipping.address_2
    
    sheet['E4'] = _('Country')
    sheet['E4'].font = Font(bold=True)
    sheet['E5'] = order.buyer.country
    
    sheet['F4'] = _('City')
    sheet['F4'].font = Font(bold=True)
    sheet['F5'] = order.buyer.city
    
    sheet['G4'] = _('Telno')
    sheet['G4'].font = Font(bold=True)
    sheet['G5'] = f'+ {order.buyer.country_code} {order.buyer.mobile_user}'

    # products
    sheet['A7'] = _('Product Name')
    sheet['A7'].font = Font(bold=True)
    sheet['B7'] = _('Quantity')
    sheet['B7'].font = Font(bold=True)
    sheet['C7'] = _('Color')
    sheet['C7'].font = Font(bold=True)
    sheet['D7'] = _('Material')
    sheet['D7'].font = Font(bold=True)
    sheet['E7'] = _('Unit Price')
    sheet['E7'].font = Font(bold=True)
    sheet['F7'] = _('Total')
    sheet['F7'].font = Font(bold=True)

    line_number = 8
    for product in SupplierModels.OrderProductVariation.objects.filter(order=order):
        sheet[f'A{line_number}'] = product.product.name
        sheet[f'B{line_number}'] = product.quantity
        sheet[f'C{line_number}'] = product.color.name
        sheet[f'D{line_number}'] = product.material.name
        sheet[f'E{line_number}'] = f"{product.price.currency} {product.price.min_price} - {product.price.max_price}"
        sheet[f'F{line_number}'] = f"{product.price.currency} {product.min_total_price} - {product.max_total_price}"        

        line_number = line_number + 1

    # Generate the file response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.xlsx"'

    # Save the workbook to the response
    workbook.save(response)

    return response