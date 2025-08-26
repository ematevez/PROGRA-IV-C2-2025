from operator import le
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
import datetime
import uuid
from coms import models as ComsModels
from auth_app import models as AuthModels
from supplier import models as SupplierModels
from django.db.models import Q
from django.conf import settings
import os

from manager import models as ManagerModels


class Notifications(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(code)

    async def notification_alerts(self, event):
        busines_pk = database_sync_to_async(self.get_business_id)()
        if busines_pk != event['target']:
            pass

        notification = event["notification"]
        title = event["title"]
        category = event["category"]

        await self.send(
            text_data=json.dumps(
                {"title": title, "category": category}
            )
        )


    def get_business_id(self):
        return self.scope['user'].business.pk

class InterChats(AsyncWebsocketConsumer):
    async def connect(self):
        # name of the chatroom
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # group users in a specific chatroom
        self.room_group_name = "inter_chats%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        await database_sync_to_async(self.createInterChatFile)(text_data_json)

        # check for status
        if text_data_json.get("status") == "load_messages":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "load_messages",
                    "data" : text_data_json
                },
            )
        elif text_data_json.get("status") == "new_message":
            
            dataObject = {
                "message": text_data_json["message"],
                "sender": text_data_json["sender"],
                "time": datetime.datetime.now().today().strftime("%Y-%m-%d %H:%M:%S")
            }
            await self.write_message_to_file(dataObject, text_data_json)

            dataObject["type"] = "interchat_message"
            dataObject["data"] = text_data_json
            await self.channel_layer.group_send(
                self.room_group_name,
                dataObject
            )
        else:
            pass
    

    async def load_messages(self, event):
        try:
            with open(event["data"].get("chat").get("chatfilepath"), "r") as file:
                current_data = json.load(file)
                for i in range(len(current_data)):
                    await self.send(text_data=json.dumps(current_data[i]))
        except FileNotFoundError:
            pass

    async def interchat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        time = event["time"]
        data = event["data"]

        await self.send(
            text_data=json.dumps(
                {"message": message, "sender": sender, "time": time}
            )
        )

        await database_sync_to_async(self.createNotification)(data)

    def createNotification(self, data):
        if data.get("type") == "business":
            chat = ComsModels.InterClientChat.objects.filter(pk=data.get("chat").get("id")).first()
        elif data.get("type") == "personal":
            chat = ComsModels.InterUserChat.objects.filter(pk=data.get("chat").get("id")).first()
        # if data.get("type") == "group"
        #     chat = ComsModels.GroupChat.objects.filter(pk=data.get("chat").get("id")).first()
        sender = AuthModels.User.objects.filter(pk=data.get("sender")).first()
        target_id = list(filter(lambda x: x != sender.business.pk, [sender.business.pk, data.get("chat").get("initiator") if data.get("chat").get("participant") == sender.business.pk else data.get("chat").get("participant")]))[0]
        target_business = AuthModels.ClientProfile.objects.filter(pk=target_id).first()

        ManagerModels.Notification.objects.create(
            target = target_business,
            title="New Chat from {}".format(sender.business.business_name),
            category="CHATS"
        )

    def createInterChatFile(self, data):
        try:
            with open(data.get("chat").get("chatfilepath"), "r") as file:
                file.close()
        except:
            with open(data.get("chat").get("chatfilepath"), "w") as file:
                json.dump([], file)

    @sync_to_async
    def write_message_to_file(self, dataObject, data):
        file_path = data.get("chat").get("chatfilepath")

        with open(file_path, "r") as file:
            current_data = json.load(file)
            current_data.append(dataObject)

        with open(file_path, "w") as file:
            json.dump(current_data, file)

class OrderChatRoom(AsyncWebsocketConsumer):
    async def connect(self):
        # name of the chatroom
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]

        # group users in a specific chatroom
        self.room_group_name = "chat_%s" % self.order_id
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "load_messages",
            },
        )

    async def load_messages(self, event):
        file_path = os.path.join(
            settings.CHATROOMFILES_DIRS.get("orders"),
            f"{self.order_id}.json",
        )

        try:
            with open(file_path, "r") as file:
                current_data = json.load(file)
                for i in range(len(current_data)):
                    await self.send(text_data=json.dumps(current_data[i]))
        except FileNotFoundError:
            pass

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        text_data_json = json.loads(text_data)
        business_id = await database_sync_to_async(self.CreateChatRecord)()
        
        dataObject = {
            "message": text_data_json["message"],
            "sender": business_id,
            "time": datetime.datetime.now().today().strftime("%Y-%m-%d %H:%M:%S")
        }
        await self.write_message_to_file(self.order_id, dataObject)

        dataObject["type"] = "order_message"
        await self.channel_layer.group_send(
            self.room_group_name,
            dataObject
        )

    async def order_message(self, event):
        message = event["message"]
        sender = event["sender"]
        time = event["time"]

        await self.send(
            text_data=json.dumps(
                {"message": message, "sender": sender, "time": time}
            )
        )

        await database_sync_to_async(self.createNotification)(sender)

    def createNotification(self, sender):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        order = SupplierModels.Order.objects.filter(order_id=self.order_id).first()
        business = AuthModels.ClientProfile.objects.filter(pk=sender).first()

        target = order.supplier if business == order.buyer else buyer
        ManagerModels.Notification.objects.create(
            target = target,
            title="New Chat on Order {}".format(self.order_id),
            category="ORDERS"
        )

    def CreateChatRecord(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        if not ComsModels.OrderChat.objects.filter(roomname=self.order_id).exists():
            # create database record
            chatroom = ComsModels.OrderChat.objects.create(
                roomname=self.order_id,
                order=SupplierModels.Order.objects.filter(order_id=self.order_id).first(),
                buyer_representative=self.scope["user"] if self.scope["user"].account_type == "BUYER" else None,
                supplier_representative=self.scope["user"] if self.scope["user"].account_type == "SUPPLIER" else None
            )
        elif (
            ComsModels.OrderChat.objects.filter(
                roomname=self.order_id,
            ).exists()
        ):
            chatroom = ComsModels.OrderChat.objects.filter(
                roomname=self.order_id,
            ).first()
            if self.scope["user"].account_type == "BUYER":
                chatroom.buyer_representative = self.scope["user"]

            if self.scope["user"].account_type == "SUPPLIER":
                chatroom.supplier_representative = self.scope["user"]

            chatroom.save()

        # return business id
        return self.scope["user"].business.pk


    @sync_to_async
    def write_message_to_file(self, unique_id, dataObject):
        file_path = os.path.join(settings.CHATROOMFILES_DIRS.get("orders"), f"{unique_id}.json")

        with open(file_path, "r") as file:
            current_data = json.load(file)
            current_data.append(dataObject)

        with open(file_path, "w") as file:
            json.dump(current_data, file)

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # name of the chatroom
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # group users in a specific chatroom
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "initial_message",
                "message": "Hello. What can I help you with?",
                "user": "support",
            },
        )

    async def initial_message(self, event):
        message = event["message"]
        user = "Support"

        await self.send(text_data=json.dumps({"message": message, "user": user}))

        file_path = os.path.join(
            settings.CHATROOMFILES_DIRS.get("support-client"),
            f"{self.scope['url_route']['kwargs']['room_name']}.json",
        )

        try:
            with open(file_path, "r") as file:
                current_data = json.load(file)
                for i in range(len(current_data)):
                    await self.send(text_data=json.dumps(current_data[i]))
        except FileNotFoundError:
            pass

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await super().disconnect(code)

    async def receive(self, text_data=None, bytes_data=None):
        roomname = self.scope["url_route"]["kwargs"]["room_name"]
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = text_data_json["user"]
        username = text_data_json["username"]

        await database_sync_to_async(self.storechatroom)(message, user, username)

        await self.write_message_to_file(roomname, {
            "user": user,
            "username": username,
            "message": message,
        })

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chatroom_message",
                "message": message,
                "username": username,
                "user": user,
            },
        )

    async def chatroom_message(self, event):
        message = event["message"]
        user = event["user"]
        username = event["username"]

        await self.send(
            text_data=json.dumps(
                {"message": message, "username": username, "user": user}
            )
        )

    def storechatroom(self, message, account_type, username):
        roomname = self.scope["url_route"]["kwargs"]["room_name"]
        user = AuthModels.User.objects.filter(username=username).first()
        if user:
            if not ComsModels.SupportClientChat.objects.filter(roomname=roomname).exists():
                # create database record
                ComsModels.SupportClientChat.objects.create(
                    roomname=roomname,
                    user=user,
                )
            elif (
                ComsModels.SupportClientChat.objects.filter(
                    Q(roomname=roomname), Q(is_handled=False)
                ).exists()
                and account_type == "Support"
            ):
                # set support handling a chat
                chatroom = ComsModels.SupportClientChat.objects.filter(
                    Q(roomname=roomname), Q(is_handled=False)
                ).first()
                user_profile = AuthModels.SupportProfile.objects.filter(
                    user=user
                ).first()

                chatroom.support = user_profile
                chatroom.is_handled = True
                chatroom.save()

                user_profile.increase_responses_count()


    @sync_to_async
    def write_message_to_file(self, unique_id, dataObject):
        file_path = os.path.join(settings.CHATROOMFILES_DIRS.get("orders"), f"{unique_id}.json")

        with open(file_path, "r") as file:
            current_data = json.load(file)
            current_data.append(dataObject)

        with open(file_path, "w") as file:
            json.dump(current_data, file)
