import os
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu import vhcm_chatbot as bot
from vhcm.models import report
from vhcm.models import chat_message
from vhcm.models import user as user_model
from vhcm.models import chat_history
from vhcm.models import train_data
from vhcm.common.constants import *
from vhcm.common.utils.files import pickle_file

# Response types
LAST_SESSION_MESSAGES = 'last_session_messages'
FORCE_NEW_SESSION = 'force_new_session'
CHAT_RESPONSE = 'chat_response'
END_SESSION_STATUS = 'end_session_status'
SERVER_ERROR = 'error'


class ChatbotConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For surpass PyCharm syntax checking
        self.user = None
        self.room_name = None
        self.room_group_name = None
        self.session_bot_version = None
        self.chatbot = None

    def connect(self):
        user_id = self.scope["session"].get('user_id')
        if not user_id:
            self.close()
            return
        user = user_model.User.objects.filter(user_id=user_id).first()
        if not user or not bot.is_bot_ready():
            self.close()
            return
        self.user = user
        self.room_name = self.user.username
        self.room_group_name = CHAT_ROOM_GROUP + self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.chatbot = bot.VirtualHCMChatbot(self.user)

        self.accept()

    def close(self, code=None):
        super().close(code)
        if hasattr(self, 'room_group_name') and self.room_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )

    def disconnect(self, close_code):
        if hasattr(self, 'room_group_name') and self.room_group_name:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        print("DISCONNECTED CODE: ", close_code)

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command')
        if command == 'newsession':
            self.start_new_session()
        elif command == 'getlastsession':
            last_session_messages = self.restore_last_session()
            self.send_response(LAST_SESSION_MESSAGES, last_session_messages)
        elif command == 'chat':
            user_input = text_data_json.get('data')
            self.chat(user_input)
        elif command == 'report':
            self.report()
        elif command == 'endsession':
            end_status = self.end_last_session()
            self.send_response(END_SESSION_STATUS, end_status)

    def restore_last_session(self):
        last_session_messages = []

        last_session = chat_message.Message.objects.filter(user=self.user).order_by(chat_message.RECORDED_TIME)
        if last_session:
            session_bot_version = last_session[0].data_version.id
            train_data_model = train_data.TrainData.objects.filter(id=session_bot_version).first()
            if not train_data_model:
                self.send_response(SERVER_ERROR)
                return
            self.session_bot_version = train_data_model
            if not bot.version_check(session_bot_version):
                self.end_last_session()
                self.send_response(FORCE_NEW_SESSION)
                return

            states = []
            for m in last_session:
                message = {
                    'sent': m.sent_from,
                    'text': m.message
                    # 'time': m.recorded_time
                }
                last_session_messages.append(message)
                if m.sent_from == chat_message.BOT_SENT:
                    states.append(bot.State(
                        bot.intent_datas[m.intent],
                        [int(i) for i in m.question_type.split(COMMA)] if m.question_type else [],
                        m.action
                    ))
            self.chatbot.state_tracker.extend(states)

        return last_session_messages

    def start_new_session(self):
        self.chatbot = bot.VirtualHCMChatbot(self.user)
        self.session_bot_version = train_data.TrainData.objects.filter(
            id=bot.system_bot_version[bot.CURRENT_BOT_VERSION]
        ).first()
        if not self.session_bot_version:
            self.send_response(SERVER_ERROR)
        if not bot.is_bot_ready():
            self.send_response(CHAT_RESPONSE, bot.BOT_UNAVAILABLE_MESSAGE)
        else:
            self.send_response(CHAT_RESPONSE, 'Chào cháu bác đêy cháu ei')

    def chat(self, user_input):
        if not bot.is_bot_ready():
            self.send_response(CHAT_RESPONSE, bot.BOT_UNAVAILABLE_MESSAGE)
            return

        if not bot.version_check(self.session_bot_version.id):
            self.end_last_session()
            self.send_response(FORCE_NEW_SESSION)
            return

        if user_input:
            self.regist_message(chat_message.USER_SENT, user_input)
            response = self.chatbot.chat(input)
            self.regist_message(chat_message.BOT_SENT, response, self.chatbot.get_last_state())
            self.send_response(CHAT_RESPONSE, response)

    # Receive message from room group
    def send_response(self, datatype, data=None):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': datatype,
            'data': data
        }))

    def regist_message(self, sent_from, message, bot_state=None):
        message_to_regist = chat_message.Message(
            user=self.user,
            sent_from=sent_from,
            message=message,
            data_version=self.session_bot_version
        )

        if bot_state:
            message_to_regist.intent = bot_state.intent.intent
            message_to_regist.question_type = COMMA.join(str(t) for t in bot_state.type) if bot_state.type else None
            message_to_regist.action = bot_state.action

        message_to_regist.save()

    def end_last_session(self):
        # Log current session
        last_session = chat_message.Message.objects.filter(user=self.user).order_by(chat_message.RECORDED_TIME)
        if last_session:
            # Messages
            session_messages = []
            for m in last_session:
                message = {
                    'from': m.sent_from,
                    'message': m.message,
                    'time': m.recorded_time.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
                }
                session_messages.append(message)
            tmp_log_path = os.path.join(PROJECT_ROOT, 'tmp/chatlog_' + self.user.username)
            pickle_file(session_messages, tmp_log_path)
            tmp_chatlog_file = open(tmp_log_path, 'rb')
            chatlog_binary = tmp_chatlog_file.read()

            # Bot data version
            session_bot_version = last_session[0].data_version

            # Session start time
            start_time = last_session[0].recorded_time

            # Regist to db
            log_model = chat_history.ChatHistory(
                user=self.user,
                log=chatlog_binary,
                data_version=session_bot_version,
                session_start=start_time
            )
            log_model.save()
            tmp_chatlog_file.close()
            # Clear session messages on DB
            last_session.delete()

        return True

    # TODO: Implement
    def report(self):
        pass
