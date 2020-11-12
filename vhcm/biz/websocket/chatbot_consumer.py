import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import vhcm.common.config.config_manager as config
from vhcm.biz.nlu.vhcm_chatbot import VirtualHCMChatbot
from vhcm.biz.authentication.user_session import get_current_user


class ChatbotConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.user = get_current_user()
        if not self.user:
            raise RuntimeError('Unexpected error occurred')
        self.chatbot = VirtualHCMChatbot(self.user)

    def connect(self):
        self.room_name = self.user.username
        self.room_group_name = 'chat_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        print("DISCONNECTED CODE: ", close_code)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json['command']

    # Receive message from room group
    def send_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': 'message',
            'data': message
        }))