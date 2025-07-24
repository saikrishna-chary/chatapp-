import json
import base64
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        file_data = data.get('file', None)
        file_url = None
        user = self.scope["user"]

        # Handle typing indicator
        if 'typing' in data:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_typing',
                    'user': user.name,
                    'typing': data['typing']
                }
            )
            return

        # Handle file if exists
        if file_data:
            format, imgstr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            file = ContentFile(base64.b64decode(imgstr), name=filename)
        else:
            file = None

        await self.save_message(user, self.room_id, message, file)

        if file:
            file_url = f"/media/chat_media/{file.name}"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user.name,
                'file_url': file_url,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'user': event['user'],
            'file_url': event.get('file_url'),
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'user': event['user'],
            'typing': event['typing']
        }))

    @database_sync_to_async
    def save_message(self, user, room_id, message, file=None):
        room = ChatRoom.objects.get(id=room_id)
        Message.objects.create(room=room, sender=user, content=message, file=file)
