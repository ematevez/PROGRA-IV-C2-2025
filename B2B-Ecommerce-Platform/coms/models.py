from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Q

import os
import uuid
import json
import datetime

# from apps
from supplier import models as SupplierModels
from auth_app import models as Authmodels


# utility functions
def get_chat_file_path(instance, chat_filename_key):
    ext = ".json"
    filename = instance.roomname
    path = os.path.join(f"{settings.CHATROOMFILES_DIRS.get(chat_filename_key)}/{filename}{ext}")
    return path

class SupportClientChat(models.Model):
    '''
        Support -Client(Buyer/Supplier Chatroom)
    '''

    chat_filename_key = "support-client"
    roomname = models.CharField(_("Chatroom Name"), max_length=256, unique=True, null=True, blank=True)
    chatfilepath = models.CharField(
        _("Chat filepath"),
        max_length=256,
        blank=True,
        null=True,
        unique=True
    )
    is_closed = models.BooleanField(_("Chat Closed"), default=False)
    is_handled = models.BooleanField(_("Chat handled"), default=False)
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)

    user = models.ForeignKey(
        Authmodels.User,
        on_delete=models.CASCADE,
    )
    support = models.ForeignKey(
        Authmodels.SupportProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    
    def save(self, *args, **kwargs):
        self.chatfilepath = get_chat_file_path(self, self.chat_filename_key)
        self.updated_on = datetime.datetime.now()
            
        # try:
        #     with open(f"{self.chatfilepath}", "w") as file:
        #         json.dump([], file)
        # except FileNotFoundError:
        #     self.chatfilepath = None

        super().save(*args, **kwargs)

# order chat in supplier models
class InterClientChat(models.Model):
    '''
        Client Chatroom
        max users: 2
    '''
    chat_filename_key = "interclient"
    roomname = models.CharField(_("Chatroom Name"), max_length=256, unique=True, null=True, blank=True)
    chatfilepath = models.CharField(
        _("Chat filepath"),
        max_length=256,
        blank=True,
        null=True,
        unique=True
    )
    is_closed = models.BooleanField(_("Chat Closed"), default=False)
    is_handled = models.BooleanField(_("Chat handled"), default=False)
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)
    initiator = models.ForeignKey(
        Authmodels.ClientProfile,
        on_delete=models.CASCADE,
        related_name="initiator"
    )
    participant = models.ForeignKey(
        Authmodels.ClientProfile,
        on_delete=models.CASCADE,
        related_name="participant"
    )
    
    def save(self, *args, **kwargs):
        self.chatfilepath = get_chat_file_path(self, self.chat_filename_key)
        self.updated_on = datetime.datetime.now()
            
        # try:
        #     with open(f"{self.chatfilepath}", "w") as file:
        #         json.dump([], file)
        # except FileNotFoundError:
        #     self.chatfilepath = None

        super().save(*args, **kwargs)

class InterUserChat(models.Model):
    '''
        Client Chatroom
        max users: 2
    '''
    chat_filename_key = "interuser"
    roomname = models.CharField(_("Chatroom Name"), max_length=256, unique=True, null=True, blank=True)
    chatfilepath = models.CharField(
        _("Chat filepath"),
        max_length=256,
        blank=True,
        null=True,
        unique=True
    )
    is_closed = models.BooleanField(_("Chat Closed"), default=False)
    is_handled = models.BooleanField(_("Chat handled"), default=False)
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)
    participants = models.ManyToManyField(to=Authmodels.User, related_name="chat_participants", blank=True)

    
    def save(self, *args, **kwargs):
        self.chatfilepath = get_chat_file_path(self, self.chat_filename_key)
        self.updated_on = datetime.datetime.now()
            
        # try:
        #     with open(f"{self.chatfilepath}", "w") as file:
        #         json.dump([], file)
        # except FileNotFoundError:
        #     self.chatfilepath = None

        super().save(*args, **kwargs)

class GroupChat(models.Model):
    '''
        Client Chatroom
        max users: 2
    '''
    chat_filename_key = "groupchat"
    roomname = models.CharField(_("Chatroom Name"), max_length=256, unique=True, null=True, blank=True)
    chatfilepath = models.CharField(
        _("Chat filepath"),
        max_length=256,
        blank=True,
        null=True,
        unique=True
    )
    is_closed = models.BooleanField(_("Chat Closed"), default=False)
    is_handled = models.BooleanField(_("Chat handled"), default=False)
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)
    name = models.CharField(_("Chatroom Name"), max_length=256, null=True, blank=True)
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to=Authmodels.get_file_path,
        blank=True,
        null=True,
        default="assets/imgs/resources/profiledefault.png",
    )
    participants = models.ManyToManyField(to=Authmodels.User, related_name="group_participants", blank=True)

    
    def save(self, *args, **kwargs):
        self.chatfilepath = get_chat_file_path(self, self.chat_filename_key)
        self.updated_on = datetime.datetime.now()
            
        # try:
        #     with open(f"{self.chatfilepath}", "w") as file:
        #         json.dump([], file)
        # except FileNotFoundError:
        #     self.chatfilepath = None

        super().save(*args, **kwargs)

class OrderChat(models.Model):
    '''
        Order Chatroom
    '''
    chat_filename_key = "orders"
    roomname = models.CharField(_("Chatroom Name"), max_length=256, unique=True, null=True, blank=True)
    chatfilepath = models.CharField(
        _("Chat filepath"),
        max_length=256,
        blank=True,
        null=True,
        unique=True
    )
    is_closed = models.BooleanField(_("Chat Closed"), default=False)
    is_handled = models.BooleanField(_("Chat handled"), default=False)
    created_on = models.DateField(_("Created on"), default=timezone.now)
    updated_on = models.DateTimeField(_("Updated on"), null=True, blank=True)
    order = models.OneToOneField(to=SupplierModels.Order, on_delete=models.CASCADE)
    
    buyer_representative = models.ForeignKey(
        Authmodels.User,
        on_delete=models.CASCADE,
        related_name="buyer_user",
        blank=True,
        null=True,
    )
    supplier_representative = models.ForeignKey(
        Authmodels.User,
        on_delete=models.CASCADE,
        related_name="supplier_user",
        blank=True,
        null=True,
    )

    
    def save(self, *args, **kwargs):
        if not self.roomname:
            self.roomname = self.order.order_id

        self.chatfilepath = get_chat_file_path(self, self.chat_filename_key)
        self.updated_on = datetime.datetime.now()
            
        # try:
        #     with open(f"{self.chatfilepath}", "w") as file:
        #         json.dump([], file)
        # except FileNotFoundError:
        #     self.chatfilepath = None

        super().save(*args, **kwargs)
