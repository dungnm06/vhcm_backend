import os
import json
import random
import traceback
from vhcm.biz.nlu.language_processing import language_processor
from vhcm.biz.nlu.classifiers.intent_classifier import IntentClassifier
from vhcm.biz.nlu.classifiers.question_type_classifier import QuestionTypeClassifier
from vhcm.biz.nlu.model.intent import Intent, load_from_data_file
from vhcm.models.knowledge_data_question import QUESTION_TYPES_IDX2T, QUESTION_TYPES_T2IDX
from vhcm.models import chat_message, train_data
from vhcm.common.constants import *

# Constants
CURRENT_BOT_VERSION = 'current'
NEXT_STARTUP_VERSION = 'next_startup'
BOT_UNAVAILABLE_MESSAGE = 'Bác đi ngủ rồi, quay lại lúc khác!'


# Chatbot state
class State(object):
    def __init__(self, intent=Intent(), type=None, action=chat_message.INITIAL):
        self.intent = intent
        self.type = type
        self.action = action


# Loadup chatbot data
def init_bot():
    try:
        # Bot version
        version_file_path = os.path.join(PROJECT_ROOT, BOT_VERSION_FILE_PATH)
        try:
            if os.path.exists(version_file_path):
                with open(version_file_path) as f:
                    version = json.load(f)
                    version[CURRENT_BOT_VERSION] = version[NEXT_STARTUP_VERSION]
            else:
                version = {
                    CURRENT_BOT_VERSION: 0,
                    NEXT_STARTUP_VERSION: 0
                }
        except IOError:
            version = {
                CURRENT_BOT_VERSION: 0,
                NEXT_STARTUP_VERSION: 0
            }

        with open(version_file_path, 'w') as f:
            json.dump(version, f, indent=4)

        # Intent classifier
        intent_classifier_instance = IntentClassifier()
        intent_classifier_instance.load()

        # Question classifier
        question_classifier_instance = QuestionTypeClassifier()
        question_classifier_instance.load()

        # Intents data
        train_data_model = train_data.TrainData.objects.filter(id=version[CURRENT_BOT_VERSION]).first()
        if not train_data_model:
            raise RuntimeError('[startup] Cannot initial bot due to invalid intents data.')
        train_data_storepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + train_data_model.filename)
        intent_data_filepath = os.path.join(train_data_storepath, INTENT_DATA_FILE_NAME)
        references_filepath = os.path.join(train_data_storepath, REFERENCES_FILE_NAME)
        synonyms_filepath = os.path.join(train_data_storepath, SYNONYMS_FILE_NAME)
        idatas = load_from_data_file(intent_data_filepath, references_filepath, synonyms_filepath)

        return intent_classifier_instance, question_classifier_instance, idatas, version
    except (RuntimeError, IOError) as e:
        # Lul
        print(e)
        print(traceback.format_exc())
        return None, None, None, version


intent_classifier, question_type_classifier, intent_datas, system_bot_version = init_bot()


def is_bot_ready():
    return system_bot_version[CURRENT_BOT_VERSION] > 0 \
           and question_type_classifier \
           and intent_classifier \
           and intent_datas


def version_check(session_bot_version):
    return system_bot_version[CURRENT_BOT_VERSION] == session_bot_version


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
                          int(self.question_id2type[t]) in intent.corresponding_datas]
        # If any of user asking data types not exist in intent so just print all intent data
        if not existing_types:
            response += (SPACE + SPACE.join(random.choice(intent.corresponding_datas[key]) for key in intent.corresponding_datas))
        else:
            response += (SPACE + SPACE.join(random.choice(intent.corresponding_datas[key]) for key in existing_types))
        return response
