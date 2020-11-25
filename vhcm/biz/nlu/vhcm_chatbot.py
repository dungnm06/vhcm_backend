import os
import json
import random
import traceback
import shutil
from vhcm.biz.nlu.language_processing import language_processor
from vhcm.biz.nlu.classifiers.intent_classifier import IntentClassifier
from vhcm.biz.nlu.classifiers.question_type_classifier import QuestionTypeClassifier
from vhcm.biz.nlu.model.intent import Intent, load_from_data_file
from vhcm.models.knowledge_data_question import QUESTION_TYPES_IDX2T, QUESTION_TYPES_T2IDX
from vhcm.models import chat_message, train_data
from vhcm.common.constants import *
from vhcm.common.utils.files import unzip, ZIP_EXTENSION

# Constants
CURRENT_BOT_VERSION = 'current'
NEXT_STARTUP_VERSION = 'next_startup'

# Messages
MESSAGE_UNAVAILABLE = 'Bác đi ngủ rồi, quay lại lúc khác!'
MESSAGE_BOT_GREATING = 'Đã bắt đầu phiên trò chuyện mới, bạn có thể chat ngay với bot'
MESSAGE_BOT_END_SESSION_SUCCESS = 'Phiên trò chuyện của bạn đã kết thúc'
MESSAGE_BOT_END_SESSION_FAILED = 'Đã có sự cố khi kết thúc phiên trò chuyện, hãy liên lạc với admin'
MESSAGE_BOT_NEW_SESSION_WAIT = 'Chatbox sẽ được làm mới trong 3s'
MESSAGE_NEW_SESSION = 'Bắt đầu phiên trò chuyện mới'
MESSAGE_BOT_FORCE_NEW_SESSION = 'Hệ thống đã có sự thay đổi dữ liệu, phiên trò chuyện của bạn đã kết thúc'
MESSAGE_CHOOSE_REPORT_TYPE = 'Hãy chọn loại báo cáo: \n1. Nội dung bot trả lời gần nhất sai.\n2. Đóng góp thông tin.\n3. Quay lại chat tiếp'
MESSAGE_INVALID_REPORT_TYPE = 'Dữ liệu không hợp lệ, hủy báo cáo.'
MESSAGE_CANCEL_REPORT = 'Hủy báo cáo, bạn có thể chat tiếp.'
MESSAGE_CHOOSE_TO_CONTRIBUTE = 'Bạn có sẵn lòng đóng góp dữ liệu cho phần này không (có/không) ?'
MESSAGE_INPUT_DATA = 'Hãy nhập vào dữ liệu: '
MESSAGE_THANK_FOR_CONTRIBUTE = 'Cảm ơn bạn đã báo cáo, dữ liệu đã được tiếp nhận. \nBạn có thể chat tiếp.'
MESSAGE_CONTINUE_TO_CHAT = 'Bạn có thể chat tiếp.'
MESSAGE_NO_DATA_TO_REPORT = 'Bot chưa ghi nhận có dữ liệu sai để tiếp nhận'
MESSAGE_INVALID_COMMAND = 'Câu lệnh không hợp lệ.'


# Chatbot state
class State(object):
    def __init__(self, intent=Intent(), question=None, answer=None, question_types=None, action=chat_message.INITIAL):
        if question_types is None:
            question_types = []
        self.intent = intent
        self.question = question
        self.answer = answer
        self.question_types = question_types
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
        # raise RuntimeError
        # Intent classifier
        intent_classifier_instance = IntentClassifier()
        intent_classifier_instance.load()

        # Question classifier
        question_classifier_instance = QuestionTypeClassifier()
        question_classifier_instance.load()

        # Intents data
        current_train_data = train_data.TrainData.objects.filter(id=version[CURRENT_BOT_VERSION]).first()
        if not current_train_data:
            raise RuntimeError('[startup] Cannot initial bot due to invalid intents data.')
        train_data_zip = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename + ZIP_EXTENSION)
        unzip(train_data_zip, output=os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER))

        train_data_storepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename)

        intent_data_filepath = os.path.join(train_data_storepath, INTENT_DATA_FILE_NAME)
        references_filepath = os.path.join(train_data_storepath, REFERENCES_FILE_NAME)
        synonyms_filepath = os.path.join(train_data_storepath, SYNONYMS_FILE_NAME)
        idatas = load_from_data_file(intent_data_filepath, references_filepath, synonyms_filepath)

        tempstorepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename)
        if os.path.exists(tempstorepath):
            shutil.rmtree(tempstorepath)

        return intent_classifier_instance, question_classifier_instance, idatas, current_train_data, version
    except (RuntimeError, IOError) as e:
        # Lul
        print(e)
        print(traceback.format_exc())
        intent_classifier_instance = None
        question_classifier_instance = None
        idatas = None
        current_train_data = None
        return intent_classifier_instance, question_classifier_instance, idatas, current_train_data, version


intent_classifier, question_type_classifier, intent_datas, train_data_model, system_bot_version = init_bot()


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
        self.user = user
        self.state_tracker = []
        # self.state_tracker.append(State())
        # Answer generator
        self.answer_generator = AnswerGenerator()
        self.train_data = train_data_model

    def __regis_history(self, intent, question, answer, question_types, action):
        self.state_tracker.append(State(intent, question, answer, question_types, action))

    def get_last_state(self):
        return self.state_tracker[len(self.state_tracker) - 1]

    def get_last_bot_answer_state_correct_answer_excluded(self):
        for idx, state in reversed(list(enumerate(self.state_tracker))):
            if state.intent and state.action in [chat_message.ANSWER, chat_message.AWAIT_CONFIRMATION]:
                if state.action == chat_message.AWAIT_CONFIRMATION:
                    user_answer_idx = idx + 1
                    if user_answer_idx < len(self.state_tracker):
                        if self.state_tracker[user_answer_idx].action == chat_message.CONFIRMATION_OK:
                            continue
                return state
        return None

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

    def chat(self, user_input=None, init=False):
        if not init:
            last_state = self.get_last_state()
            if last_state.action != chat_message.AWAIT_CONFIRMATION:
                intent_name = intent_classifier.predict(user_input)
                types = question_type_classifier.predict(user_input)
                intent = intent_datas[intent_name]
            else:
                intent = last_state.intent
                types = last_state.question_types
            action = self.__decide_action(user_input, intent, types, last_state)
            # print(action)
            bot_response = self.answer_generator.get_response(intent, types, action, last_state)
            self.__regis_history(intent, user_input, bot_response, types, action)
        else:
            bot_response = MESSAGE_BOT_GREATING
            self.__regis_history(Intent(), None, bot_response, [], chat_message.INITIAL)
        return bot_response


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
            return self.answer(last_state.intent, last_state.question_types)
        elif action == chat_message.CONFIRMATION_NG:
            return self.confirmation_ng()

    @staticmethod
    def confirmation(intent):
        return 'Có phải bạn đang hỏi về: ' + intent.fullname + '? (đúng, sai)'

    @staticmethod
    def confirmation_ng():
        return MESSAGE_CHOOSE_TO_CONTRIBUTE

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

# from keras.backend.tensorflow_backend import set_session
# from keras.backend.tensorflow_backend import clear_session
# from keras.backend.tensorflow_backend import get_session
# import tensorflow
# import gc
#
# # Reset Keras Session
# def reset_keras():
#     sess = get_session()
#     clear_session()
#     sess.close()
#     sess = get_session()
#
#     try:
#         del classifier # this is from global space - change this as you need
#     except:
#         pass
#
#     print(gc.collect()) # if it does something you should see a number as output
#
#     # use the same config as you used to create the session
#     config = tensorflow.ConfigProto()
#     config.gpu_options.per_process_gpu_memory_fraction = 1
#     config.gpu_options.visible_device_list = "0"
#     set_session(tensorflow.Session(config=config))
