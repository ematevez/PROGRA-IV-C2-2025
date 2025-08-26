# django
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

# apps
from auth_app.models import  ClientProfile


# class WishList(models.Model):
#     buyer = models.ForeignKey(to=Buyer, on_delete=models.CASCADE)
#     created_on = models.DateField(_("Created on"), default=timezone.now)

#     def __str__(self) -> str:
#         return f"Buyer: {self.buyer.username} - Product: {self.product.name}"

class Cart(models.Model):
    buyer = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE)
    created_on = models.DateField(_("Created on"), default=timezone.now)

# SIGNALS
# @receiver(post_save, sender=WishList)
# def on_wishlist_save(sender, instance, **kwargs):
#     # send supplier email
#     pass


# class Bid(models.Model):
#     buyer = models.ForeignKey(to=ClientProfile, on_delete=models.CASCADE)