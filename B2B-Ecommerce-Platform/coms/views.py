from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.db.models import Q
import uuid
from auth_app import models as AuthModels
from coms import models as ComsModels

from coms import tasks as ComsTasks
from django.contrib import messages

class InterClientChatInitView(View):
    def get(self, request, business_slug):
        business = AuthModels.ClientProfile.objects.filter(user=request.user)
        target_business = get_object_or_404(AuthModels.ClientProfile, slug=business_slug)
        if not business:
            return redirect(reverse("manager:dashboard"))
        else:
            business = business.first()

        # does one exist
        chat = ComsModels.InterClientChat.objects.filter(
            Q(initiator=business, participant=target_business)
            | Q(participant=business, initiator=target_business)
        )
        if chat:
            chat = chat.first()
        else:
            # create chat
            chat = ComsModels.InterClientChat.objects.create(
                initiator = business,
                participant = target_business,
                roomname=uuid.uuid4()
            )
            ComsTasks.notify_participant.delay(chat.pk, "Chat created")
        
        return redirect(reverse("buyer:messenger"))

class GroupChatAppendView(View):
    def get(self, request, roomname):
        if request.user.is_authenticated:
            record = ComsModels.GroupChat.objects.filter(roomname=roomname)
            if not record:
                messages.add_message(request, messages.ERROR, _("Record Not Fount."))
                return redirect(reverse("manager:home"))
            record.first().participants.add(request.user)
            messages.add_message(request, messages.SUCCESS, _("Visit you dashboard to chat."))
            return redirect(reverse("manager:dashboard"))

        messages.add_message(request, messages.ERROR, _("Sign in to continue."))
        return redirect(reverse("auth_app:login"))
