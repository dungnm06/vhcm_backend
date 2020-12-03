import os
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from vhcm.biz.nlu import vhcm_chatbot as bot
from vhcm.models import report as report_model
from vhcm.models import chat_state
from vhcm.models import user as user_model
from vhcm.models import chat_history
from vhcm.models import train_data
from vhcm.common.constants import *
from vhcm.common.utils.files import pickle_file
from vhcm.common.utils.CH import isInt

# Response types
LAST_SESSION_MESSAGES = 'last_session_messages'
FORCE_NEW_SESSION = 'force_new_session'
CHAT_RESPONSE = 'chat_response'
END_SESSION_STATUS = 'end_session_status'
SERVER_ERROR = 'error'
CHOOSE_REPORT_TYPE = 'choose_report_type'
CHOOSE_TO_CONTRIBUTE = 'choose_to_contribute'
INPUT_DATA = 'input_data'
INPUT_REFERENCE = 'input_reference'
CHOOSE_TO_INPUT_NOTE = 'input_note'

# Command types
COMMAND_START_NEW_SESSION = 'newsession'
COMMAND_REPORT = 'report'
COMMAND_END_SESSION = 'endsession'

# Report processing
REPORT = 1
# All report choices
REPORT_WRONG_ANSWER = report_model.WRONG_ANSWER
REPORT_CONTRIBUTE_DATA = report_model.CONTRIBUTE_DATA
REPORT_CANCEL = 3
ANSWER_CONFIRMATION_NG = 4
ACTION_TYPES = [
    REPORT_WRONG_ANSWER,
    REPORT_CONTRIBUTE_DATA,
    REPORT_CANCEL,
    ANSWER_CONFIRMATION_NG
]
REGIST_BOT_STATE_TYPES = [
    REPORT_WRONG_ANSWER,
    ANSWER_CONFIRMATION_NG
]
YESNO_REPONSES = [
    CHOOSE_TO_CONTRIBUTE,
    CHOOSE_TO_INPUT_NOTE
]
# Message mapping
ACTION_RESPONSES = {
    CHOOSE_REPORT_TYPE: bot.MESSAGE_CHOOSE_REPORT_TYPE,
    CHOOSE_TO_CONTRIBUTE: bot.MESSAGE_CHOOSE_TO_CONTRIBUTE,
    INPUT_DATA: bot.MESSAGE_INPUT_DATA,
    INPUT_REFERENCE: bot.MESSAGE_INPUT_REFERENCE,
    CHOOSE_TO_INPUT_NOTE: bot.MESSAGE_CHOOSE_TO_INPUT_NOTE,
}
# Report process states
PROCESSING_REPORT_WRONG_ANSWER = [
    CHOOSE_REPORT_TYPE,
    CHOOSE_TO_CONTRIBUTE,
    INPUT_DATA,
    CHOOSE_TO_INPUT_NOTE,
    INPUT_DATA
]
PROCESSING_CONTRIBUTE_DATA = [
    CHOOSE_REPORT_TYPE,
    INPUT_DATA,
    CHOOSE_TO_INPUT_NOTE,
    INPUT_DATA
]
PROCESSING_ANSWER_CONFIRMATION_NG = [
    CHOOSE_TO_CONTRIBUTE,
    INPUT_DATA,
    CHOOSE_TO_INPUT_NOTE,
    INPUT_DATA
]
ACTION_TYPES_MAP = {
    REPORT_WRONG_ANSWER: PROCESSING_REPORT_WRONG_ANSWER,
    REPORT_CONTRIBUTE_DATA: PROCESSING_CONTRIBUTE_DATA,
    REPORT_CANCEL: None,
    ANSWER_CONFIRMATION_NG: PROCESSING_ANSWER_CONFIRMATION_NG
}


class ChatbotConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # For surpass PyCharm syntax checking
        self.user = None
        self.room_name = None
        self.room_group_name = None
        self.session_bot_version = None
        self.chatbot = None
        self.last_state = None
        self.state_idx = None
        self.input_data_type = None
        self.processing_type = None
        self.processing_report_type = None
        self.report_data = None
        self.report_note = None
        self.bot_state_to_regist = None
        self.bot_state_to_regist_idx = None
        self.answer_ng_user_choosen_to_contribute = False

    def connect(self):
        user_id = self.scope["session"].get('user_id')
        if not user_id:
            self.close()
            return
        user = user_model.User.objects.filter(user_id=user_id).first()
        if not user:
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
        if not bot.is_bot_ready():
            self.send_error()
            return
        text_data_json = json.loads(text_data)
        command = text_data_json.get('command')
        if command == 'newsession':
            self.start_new_session()
        elif command == 'getlastsession':
            last_session_messages = self.restore_last_session()
            if last_session_messages['return_data']:
                self.send_response(LAST_SESSION_MESSAGES, last_session_messages['last_session_messages'])
        elif command == 'chat' and text_data_json.get('data'):
            user_input = text_data_json.get('data')
            self.regist_message(chat_state.USER_SENT, user_input)
            # User sending command
            if user_input.startswith(EXCLAMATION):
                command = user_input[1:]
                if command == COMMAND_START_NEW_SESSION:
                    self.send_new_session()
                elif command == COMMAND_END_SESSION:
                    self.send_end_session()
                elif command == COMMAND_REPORT:
                    self.last_state = CHOOSE_REPORT_TYPE
                    self.processing_type = REPORT
                    self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_CHOOSE_REPORT_TYPE)
                    self.send_response(CHAT_RESPONSE, bot.MESSAGE_CHOOSE_REPORT_TYPE)
                else:
                    self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_INVALID_COMMAND)
                    self.send_response(CHAT_RESPONSE, bot.MESSAGE_INVALID_COMMAND)
            elif self.last_state in ACTION_RESPONSES:
                # User sending command to use system functions
                # Report
                if self.processing_type == REPORT:
                    # User is choosing report type
                    if self.processing_report_type is None:
                        if not isInt(user_input) and int(user_input) not in ACTION_TYPES:
                            self.error_cancel_report()
                            return
                        user_input = int(user_input)
                        # Wrong answer report
                        if user_input == REPORT_WRONG_ANSWER:
                            bot_state_to_regist, self.bot_state_to_regist_idx = self.chatbot.get_last_report_able_state()
                            if not bot_state_to_regist:
                                self.reset_system_communicate_state()
                                self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_NO_DATA_TO_REPORT)
                                self.send_response(CHAT_RESPONSE, bot.MESSAGE_NO_DATA_TO_REPORT)
                                return
                            self.bot_state_to_regist = bot_state_to_regist
                            self.processing_report_type = REPORT_WRONG_ANSWER
                            self.state_idx = 1
                            self.last_state = PROCESSING_REPORT_WRONG_ANSWER[self.state_idx]
                            self.regist_message(chat_state.SYSTEM_SENT, ACTION_RESPONSES[self.last_state])
                            self.send_response(CHAT_RESPONSE, ACTION_RESPONSES[self.last_state])
                        elif user_input == REPORT_CONTRIBUTE_DATA:
                            # Contribute data
                            self.processing_report_type = REPORT_CONTRIBUTE_DATA
                            self.state_idx = 1
                            self.last_state = PROCESSING_CONTRIBUTE_DATA[self.state_idx]
                            self.regist_message(chat_state.SYSTEM_SENT, ACTION_RESPONSES[self.last_state])
                            self.send_response(CHAT_RESPONSE, ACTION_RESPONSES[self.last_state])
                        elif user_input == REPORT_CANCEL:
                            # Cancel report
                            self.reset_system_communicate_state()
                            self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_CANCEL_REPORT)
                            self.send_response(CHAT_RESPONSE, bot.MESSAGE_CANCEL_REPORT)
                    else:
                        # User filling report data
                        if self.processing_report_type == REPORT_WRONG_ANSWER:
                            self.state_idx += 1
                            if self.last_state == INPUT_DATA:
                                if self.input_data_type == CHOOSE_TO_INPUT_NOTE:
                                    self.report_note = user_input
                                elif self.input_data_type == CHOOSE_TO_CONTRIBUTE:
                                    self.report_data = user_input
                            elif self.last_state in YESNO_REPONSES:
                                if user_input == 'có' or user_input == 'co':
                                    pass
                                elif user_input == 'không' or user_input == 'khong':
                                    self.state_idx += 1
                                else:
                                    self.error_cancel_report()
                                    return
                                self.input_data_type = self.last_state
                            if self.state_idx >= len(PROCESSING_REPORT_WRONG_ANSWER):
                                self.regist_report(bot_state=self.bot_state_to_regist)
                                self.reset_system_communicate_state()
                                self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_THANK_FOR_CONTRIBUTE)
                                self.send_response(CHAT_RESPONSE, bot.MESSAGE_THANK_FOR_CONTRIBUTE)
                                return
                            self.last_state = PROCESSING_REPORT_WRONG_ANSWER[self.state_idx]
                            self.regist_message(chat_state.SYSTEM_SENT, ACTION_RESPONSES[self.last_state])
                            self.send_response(CHAT_RESPONSE, ACTION_RESPONSES[self.last_state])
                        elif self.processing_report_type == REPORT_CONTRIBUTE_DATA:
                            self.state_idx += 1
                            if self.last_state == INPUT_DATA:
                                self.report_data = user_input
                            if self.state_idx == len(PROCESSING_CONTRIBUTE_DATA):
                                self.regist_report()
                                self.reset_system_communicate_state()
                                self.regist_message(
                                    chat_state.SYSTEM_SENT,
                                    bot.MESSAGE_THANK_FOR_CONTRIBUTE)
                                self.send_response(CHAT_RESPONSE, bot.MESSAGE_THANK_FOR_CONTRIBUTE)
                                return
                            self.last_state = PROCESSING_REPORT_WRONG_ANSWER[self.state_idx]
                            self.regist_message(chat_state.SYSTEM_SENT, ACTION_RESPONSES[self.last_state])
                            self.send_response(CHAT_RESPONSE, ACTION_RESPONSES[self.last_state])
                        elif self.processing_report_type == ANSWER_CONFIRMATION_NG:
                            self.state_idx += 1
                            if self.last_state == INPUT_DATA:
                                if self.input_data_type == CHOOSE_TO_INPUT_NOTE:
                                    self.report_note = user_input
                                elif self.input_data_type == CHOOSE_TO_CONTRIBUTE:
                                    self.report_data = user_input
                            elif self.last_state in YESNO_REPONSES:
                                user_input = user_input.lower()
                                if user_input == 'có' or user_input == 'co':
                                    self.answer_ng_user_choosen_to_contribute = True
                                    if self.last_state == CHOOSE_TO_CONTRIBUTE:
                                        self.bot_state_to_regist, self.bot_state_to_regist_idx = self.chatbot.get_last_report_able_state()
                                    pass
                                elif user_input == 'không' or user_input == 'khong':
                                    self.answer_ng_user_choosen_to_contribute = False
                                    self.state_idx += 1
                                else:
                                    self.error_cancel_report()
                                    return
                                self.input_data_type = self.last_state
                            if self.state_idx == len(PROCESSING_ANSWER_CONFIRMATION_NG):
                                self.regist_report(bot_state=self.bot_state_to_regist)
                                if self.answer_ng_user_choosen_to_contribute:
                                    response_message = bot.MESSAGE_THANK_FOR_CONTRIBUTE
                                else:
                                    response_message = bot.MESSAGE_CONTINUE_TO_CHAT
                                self.reset_system_communicate_state()
                                self.regist_message(
                                    chat_state.SYSTEM_SENT,
                                    response_message)
                                self.send_response(CHAT_RESPONSE, response_message)
                                return
                            self.last_state = PROCESSING_ANSWER_CONFIRMATION_NG[self.state_idx]
                            self.regist_message(chat_state.SYSTEM_SENT, ACTION_RESPONSES[self.last_state])
                            self.send_response(CHAT_RESPONSE, ACTION_RESPONSES[self.last_state])
            else:
                response = self.chat(user_input)
                if response.get('command'):
                    command = response['command']
                    if command == FORCE_NEW_SESSION:
                        self.send_force_new_session()
                    elif command == SERVER_ERROR:
                        self.send_error()
                else:
                    self.regist_message(chat_state.BOT_SENT, response['message'], self.chatbot.get_last_state())
                    self.send_response(CHAT_RESPONSE, response['message'])

    def restore_last_session(self):
        last_session_messages = []

        last_session = chat_state.ChatState.objects.filter(user=self.user).order_by(chat_state.RECORDED_TIME)
        if last_session:
            session_bot_version = last_session[0].data_version.id
            train_data_model = train_data.TrainData.objects.filter(id=session_bot_version).first()
            if not train_data_model:
                self.send_error()
                return {
                    'last_session_messages': None,
                    'return_data': False
                }
            self.session_bot_version = train_data_model
            if not bot.version_check(session_bot_version):
                self.send_force_new_session()
                return {
                    'last_session_messages': None,
                    'return_data': False
                }

            states = []
            for m in last_session:
                message = {
                    'sent': m.sent_from,
                    'text': m.message
                    # 'time': m.recorded_time
                }
                last_session_messages.append(message)
                if m.sent_from == chat_state.BOT_SENT:
                    if m.predicted_intent:
                        states.append(bot.State(
                            bot.intent_datas[m.predicted_intent],
                            m.user_question,
                            m.message,
                            [int(i) for i in m.question_type.split(COMMA)] if m.question_type else [],
                            m.action
                        ))
                    else:
                        states.append(bot.State())
                if m.sent_from == chat_state.SYSTEM_SENT:
                    self.state_idx = m.system_state_idx
                    self.processing_type = m.system_processing_type
                    self.processing_report_type = m.system_processing_report_type
                    if self.state_idx and self.processing_report_type:
                        self.last_state = ACTION_TYPES_MAP[self.processing_report_type][self.state_idx]
                    self.input_data_type = m.system_input_data_type
                    self.report_data = m.system_tmp_report_data
                    self.report_note = m.system_tmp_report_note
                    self.bot_state_to_regist_idx = m.system_tmp_report_bot_state
                    self.answer_ng_user_choosen_to_contribute = m.system_tmp_user_choose_to_contribute
                    if self.bot_state_to_regist_idx:
                        self.bot_state_to_regist = states[self.bot_state_to_regist_idx]
            self.chatbot.state_tracker.extend(states)
            self.chatbot.extract_reportable_states(last_session.reverse()[0].reportable_bot_states)
        return {
            'last_session_messages': last_session_messages,
            'return_data': True
        }

    def start_new_session(self):
        self.chatbot = bot.VirtualHCMChatbot(self.user)
        self.session_bot_version = train_data.TrainData.objects.filter(
            id=bot.system_bot_version[bot.CURRENT_BOT_VERSION]
        ).first()
        if not bot.is_bot_ready() or not self.session_bot_version:
            self.send_error()
        else:
            self.send_greeting()

    def chat(self, user_input):
        if not bot.is_bot_ready():
            return {
                'command': SERVER_ERROR,
                'message': [bot.MESSAGE_UNAVAILABLE]
            }

        if not bot.version_check(self.session_bot_version.id):
            return {
                'command': FORCE_NEW_SESSION
            }

        if user_input:
            bot_response = self.chatbot.chat(user_input)
            last_bot_state = self.chatbot.get_last_state()
            if last_bot_state.action == chat_state.CONFIRMATION_NG:
                # Enter report mode
                self.processing_type = REPORT
                self.state_idx = 0
                self.last_state = PROCESSING_ANSWER_CONFIRMATION_NG[self.state_idx]
                self.processing_report_type = ANSWER_CONFIRMATION_NG
            return {
                'command': None,
                'message': bot_response
            }

    # Receive message from room group
    def send_response(self, datatype, data=None):
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'type': datatype,
            'data': data
        }))

    def send_force_new_session(self):
        self.end_last_session()
        self.regist_message(
            chat_state.SYSTEM_SENT,
            bot.MESSAGE_BOT_FORCE_NEW_SESSION
        )
        self.send_response(FORCE_NEW_SESSION, [bot.MESSAGE_BOT_FORCE_NEW_SESSION])

    def send_error(self):
        self.send_response(SERVER_ERROR, [bot.MESSAGE_UNAVAILABLE])

    def send_greeting(self):
        bot_greeting = self.chatbot.chat(init=True)
        self.regist_message(
            chat_state.BOT_SENT,
            bot_greeting
        )
        self.send_response(CHAT_RESPONSE, bot_greeting)

    def send_end_session(self):
        end_status = self.end_last_session()
        if end_status:
            messages = [bot.MESSAGE_BOT_END_SESSION_SUCCESS]
        else:
            messages = [bot.MESSAGE_BOT_END_SESSION_FAILED]
        self.send_response(END_SESSION_STATUS, {
            'end_status': end_status,
            'messages': messages,
            'start_new': False
        })

    def send_new_session(self):
        end_status = self.end_last_session()
        if end_status:
            messages = [bot.MESSAGE_BOT_END_SESSION_SUCCESS, bot.MESSAGE_BOT_NEW_SESSION_WAIT]
        else:
            messages = [bot.MESSAGE_BOT_END_SESSION_FAILED]
        self.send_response(END_SESSION_STATUS, {
            'end_status': end_status,
            'messages': messages,
            'start_new': True
        })

    def reset_system_communicate_state(self):
        self.state_idx = None
        self.last_state = None
        self.processing_report_type = None
        self.processing_type = None
        self.report_data = None
        self.report_note = None
        self.input_data_type = None
        self.bot_state_to_regist = None
        self.bot_state_to_regist_idx = None
        self.answer_ng_user_choosen_to_contribute = None

    def error_cancel_report(self):
        self.reset_system_communicate_state()
        self.regist_message(chat_state.SYSTEM_SENT, bot.MESSAGE_INVALID_REPORT_TYPE)
        self.send_response(CHAT_RESPONSE, bot.MESSAGE_INVALID_REPORT_TYPE)

    def regist_message(self, sent_from, message, bot_state=None):
        message_to_regist = chat_state.ChatState(
            user=self.user,
            sent_from=sent_from,
            message=message,
            data_version=self.chatbot.train_data,
            reportable_bot_states=self.chatbot.report_able_states_to_db_data()
        )

        if sent_from == chat_state.SYSTEM_SENT:
            message_to_regist.system_state_idx = self.state_idx
            message_to_regist.system_processing_type = self.processing_type
            message_to_regist.system_processing_report_type = self.processing_report_type
            message_to_regist.system_input_data_type = self.input_data_type
            message_to_regist.system_tmp_report_note = self.report_note
            message_to_regist.system_tmp_report_data = self.report_data
            message_to_regist.system_tmp_report_bot_state = self.bot_state_to_regist_idx
            message_to_regist.system_tmp_user_choose_to_contribute = self.answer_ng_user_choosen_to_contribute

        if bot_state:
            message_to_regist.predicted_intent = bot_state.intent.intent
            message_to_regist.user_question = bot_state.question
            message_to_regist.question_type = COMMA.join(str(t) for t in bot_state.question_types) if bot_state.question_types else None
            message_to_regist.action = bot_state.action

        message_to_regist.save()

    def end_last_session(self):
        # Log current session
        last_session = chat_state.ChatState.objects.filter(user=self.user).order_by(chat_state.RECORDED_TIME)
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
            os.remove(tmp_log_path)
            # Clear session messages on DB
            last_session.delete()

        return True

    def regist_report(self, bot_state=None):
        if self.processing_report_type == ANSWER_CONFIRMATION_NG or self.processing_report_type == REPORT_WRONG_ANSWER:
            report_type = 1
        else:
            report_type = 2
        report = report_model.Report(
            reporter=self.user,
            report_data=self.report_data,
            reporter_note=self.report_note,
            type=report_type,
            status=report_model.PENDING,
            bot_version=self.chatbot.train_data
        )
        if self.processing_report_type in REGIST_BOT_STATE_TYPES and bot_state:
            report.reported_intent = bot_state.intent.intent
            report.question = bot_state.question
            report.bot_answer = bot_state.answer
        report.save()
