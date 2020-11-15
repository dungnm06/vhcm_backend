from vhcm.biz.nlu.language_processing import language_processor
from vhcm.biz.nlu.classifiers.intent_classifier import predict_instance as intent_classifier
from vhcm.biz.nlu.classifiers.question_type_classifier import predict_instance as question_type_classifier
from vhcm.biz.nlu.model.intent import Intent
from vhcm.models.knowledge_data_question import QUESTION_TYPES_IDX2T, QUESTION_TYPES_T2IDX
from vhcm.models import chat_message
from vhcm.common.state.state_manager import state_manager

# Constants
CURRENT_BOT_VERSION = 'current_bot_version'
BOT_UNAVAILABLE_MESSAGE = 'Bác đi ngủ rồi, quay lại lúc khác!'

# Bot version
system_bot_version = int(state_manager.get_state(CURRENT_BOT_VERSION, 0))


# Chatbot state
class State(object):
    def __init__(self, intent=Intent(), type=None, action=chat_message.INITIAL):
        self.intent = intent
        self.type = type
        self.action = action


# TODO: Load intent data
intent_datas = {}


def is_bot_ready():
    return system_bot_version > 0 and question_type_classifier and intent_classifier


def version_check(session_bot_version):
    return system_bot_version == session_bot_version


class VirtualHCMChatbot(object):
    def __init__(self, user):
        # For dialogue states tracking (list of dictionary(intent,types,action))
        self.state_tracker = []
        self.state_tracker.append(State())
        # Answer generator
        self.answer_generator = AnswerGenerator()

    def __regis_history(self, intent, types, action):
        self.state_tracker.append(State(intent, types, action))

    def get_last_state(self):
        return self.state_tracker[len(self.state_tracker) - 1]

    @staticmethod
    def __decide_action(chat_input, intent, types, last_state):
        """Combines intent and question type recognition to decide bot action"""
        # print(last_state)
        if intent.intent_id == last_state.intent.intent_id and last_state.action == chat_message.AWAIT_CONFIRMATION:
            if chat_input.lower() == 'đúng':
                return chat_message.CONFIRMATION_OK
            else:
                return chat_message.CONFIRMATION_NG
        else:
            if language_processor.analyze_sentence_components(intent, chat_input):
                return chat_message.ANSWER
            else:
                return chat_message.AWAIT_CONFIRMATION

    def chat(self, chat_input):
        last_state = self.get_last_state()
        if last_state.action != chat_message.AWAIT_CONFIRMATION:
            intent_name = intent_classifier.predict(chat_input)
            types = question_type_classifier.predict(chat_input)
            intent = intent_datas[intent_name]
        else:
            intent = last_state.intent
            types = last_state.type
        action = self.__decide_action(chat_input, intent, types, last_state)
        # print(action)
        self.__regis_history(intent, types, action)
        return self.answer_generator.get_response(intent, types, action, last_state)


class AnswerGenerator:
    def __init__(self):
        self.question_id2type = QUESTION_TYPES_IDX2T
        self.question_type2id = QUESTION_TYPES_T2IDX

    def get_response(self, intent, types, action, last_state):
        if action == chat_message.ANSWER:
            return self.answer(intent, types)
        elif action == chat_message.AWAIT_CONFIRMATION:
            return self.confirmation(intent)
        elif action == chat_message.CONFIRMATION_OK:
            return self.answer(last_state[0], last_state[1])
        elif action == chat_message.CONFIRMATION_NG:
            return self.confirmation_ng()

    @staticmethod
    def confirmation(intent):
        return 'Có phải bạn đang hỏi về: ' + intent.name + '? (đúng, sai)'

    @staticmethod
    def confirmation_ng():
        return 'Hiện tại chức năng báo cáo chưa hoàn thiện, mời bạn hỏi lại câu mới!'

    def answer(self, intent, types):
        response = intent.base_response
        # Get type data exists in intent
        existing_types = [int(self.question_type2id[t]) for t in types if
                          int(self.question_id2type[t]) in intent.intent_types]
        # If any of user asking data types not exist in intent so just print all intent data
        if not existing_types:
            existing_types = intent.intent_types
        for t in existing_types:
            response += (' ' + intent.corresponding_datas[t])
        return response
