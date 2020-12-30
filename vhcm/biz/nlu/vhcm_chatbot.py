import os
import json
import random
import shutil
import tensorflow as tf
from vhcm.biz.nlu.language_processing import language_processor
from vhcm.biz.nlu.classifiers.intent_classifier import IntentClassifier
from vhcm.biz.nlu.classifiers.question_type_classifier import QuestionTypeClassifier
from vhcm.biz.nlu.classifiers.out_of_scope_intent_recognizer import OutOfScopeIntentRecognizer, HCM_QUESTION, OUT_OF_SCOPE_DIALOGUE
from vhcm.biz.nlu.classifiers.context_question_recognizer import ContextQuestionRecognizer, CONTEXT_QUESTION
from vhcm.biz.nlu.model.intent import Intent, load_from_data_file
from vhcm.models.knowledge_data_question import QUESTION_TYPES_IDX2T, QUESTION_TYPES_T2IDX
from vhcm.models import chat_state, train_data
from vhcm.common.constants import *
from vhcm.common.utils.files import unzip, ZIP_EXTENSION

# Constants
CURRENT_BOT_VERSION = 'current'
NEXT_STARTUP_VERSION = 'next_startup'
TURN_OFF_NEXT_STARTUP = 'turn_off_next_startup'

# Messages
MESSAGE_UNAVAILABLE = 'Chatbot hiện tại không khả dụng, mời bạn quay lại lúc khác!'
MESSAGE_BOT_GREATING = 'Đã bắt đầu phiên trò chuyện mới, bạn có thể chat ngay với bot\nNhập !help để xem các câu lệnh.'
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
MESSAGE_THANK_FOR_CONTRIBUTE = 'Cảm ơn bạn báo cáo, dữ liệu đã được tiếp nhận. \nBạn có thể chat tiếp.'
MESSAGE_CONTINUE_TO_CHAT = 'Bạn có thể chat tiếp.'
MESSAGE_NO_DATA_TO_REPORT = 'Bot chưa ghi nhận có dữ liệu sai để tiếp nhận'
MESSAGE_INVALID_COMMAND = 'Câu lệnh không hợp lệ.'
MESSAGE_INPUT_REFERENCE = 'Xin bạn hãy cho biết nguồn của thông tin:'
MESSAGE_CHOOSE_TO_INPUT_NOTE = 'Bạn có note thêm gì không (có/không) ?'
MESSAGE_VIEW_LIST_COMMAND = '''Danh sách các câu lệnh:
!help: xem danh sách các câu lệnh
!report: báo cáo dữ liệu sai, đóng góp thông tin
!reference: xem nguồn của câu trả lời gần nhất
!newsession: làm mới khung chat, bắt đầu phiên trò chuyện mới
'''
MESSAGE_VIEW_REFERENCE = '''Tên tri thức: {intent_name}
Nguồn:
{references}
'''
MESSAGE_REFERENCE_INFO = '''{idx}{reference_name}\n{reference_author}{reference_info}'''
MESSAGE_BOT_DIDNOT_ANSWER_ANYTHING_YET = 'Bot đã trả lời bạn thông tin gì đâu !?'
MESSAGE_NOTHING_TO_ANSWER = 'Bạn đang hỏi về vấn đề gì ?'
MESSAGE_USER_INPUT_UNKNOW_COMMAND = 'Sai cú pháp, đã hủy thao tác trước đó.\nBạn có thể chat tiếp.'
MESSAGE_OOS_ANSWER = 'Xin lỗi hình như vấn đề này bot không có thông tin nên không thể trả lời bạn được, mời bạn hỏi câu khác.'
MESSAGE_CONFIRMATION = 'Có phải bạn đang hỏi về: {intent}? (đúng, sai)'
MESSAGE_CANCER_LAST_COMMAND = 'Đã huỷ thao tác trước đó.'


# Chatbot state
class State(object):
    def __init__(self, intent=Intent(), question=None, answer=None, question_types=None, hcm_question=False, context_question=False, action=chat_state.INITIAL):
        if question_types is None:
            question_types = []
        self.intent = intent
        self.question = question
        self.answer = answer
        self.question_types = question_types
        self.hcm_question = hcm_question
        self.context_question = context_question
        self.action = action


# Loadup chatbot data
def init_bot():
    try:
        # Bot version
        version_file_path = os.path.join(PROJECT_ROOT, BOT_VERSION_FILE_PATH)
        turnoff_bot_flag = False
        if os.path.exists(version_file_path):
            with open(version_file_path) as f:
                version = json.load(f)
                version[CURRENT_BOT_VERSION] = version[NEXT_STARTUP_VERSION]
                turnoff_bot_flag = version[TURN_OFF_NEXT_STARTUP]
                version[TURN_OFF_NEXT_STARTUP] = False
        else:
            version = {
                CURRENT_BOT_VERSION: 0,
                NEXT_STARTUP_VERSION: 0,
                TURN_OFF_NEXT_STARTUP: False
            }

        with open(version_file_path, 'w') as f:
            json.dump(version, f, indent=4)

        if turnoff_bot_flag:
            raise RuntimeError('[startup] Chatbot has been flagged to turn off')
        if version[CURRENT_BOT_VERSION] == 0:
            raise RuntimeError('[startup] Could not initial chatbot (Bot version: 0)')

        # Intents data
        current_train_data = train_data.TrainData.objects.filter(id=version[CURRENT_BOT_VERSION]).first()
        if not current_train_data:
            raise RuntimeError('[startup] Cannot initial bot due to invalid intents data.')
        train_data_zip = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename + ZIP_EXTENSION)
        if not os.path.exists(train_data_zip):
            raise RuntimeError('[startup] Cannot initial bot due to missing intents data.')
        unzip(train_data_zip, output=os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER))

        # raise RuntimeError
        # Intent classifier
        intent_classifier_instance = IntentClassifier()
        intent_classifier_instance.load()

        # Question type classifier
        question_classifier_instance = QuestionTypeClassifier()
        question_classifier_instance.load()

        # Dialogue intent recognizer
        oos_intent_recognizer_instance = OutOfScopeIntentRecognizer()
        oos_intent_recognizer_instance.load()

        # Context question recognizer
        context_question_recognizer_instance = ContextQuestionRecognizer()
        context_question_recognizer_instance.load()

        train_data_storepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename)

        intent_data_filepath = os.path.join(train_data_storepath, INTENT_DATA_FILE_NAME)
        references_filepath = os.path.join(train_data_storepath, REFERENCES_FILE_NAME)
        synonyms_filepath = os.path.join(train_data_storepath, SYNONYMS_FILE_NAME)
        idatas, documents = load_from_data_file(intent_data_filepath, references_filepath, synonyms_filepath)

        tempstorepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + current_train_data.filename)
        if os.path.exists(tempstorepath):
            shutil.rmtree(tempstorepath)

        return intent_classifier_instance, question_classifier_instance, idatas, documents, oos_intent_recognizer_instance, context_question_recognizer_instance, current_train_data, version
    except Exception as e:
        # Lul
        print(e)
        # print(traceback.format_exc())
        tf.keras.backend.clear_session()
        version = {
            CURRENT_BOT_VERSION: 0,
            NEXT_STARTUP_VERSION: 0,
            TURN_OFF_NEXT_STARTUP: False
        }
        return None, None, None, None, None, None, None, version


intent_classifier, question_type_classifier, intent_datas, documents_data, oos_intent_recognizer, context_question_recognizer, train_data_model, system_bot_version = init_bot()


def is_bot_ready():
    return system_bot_version[CURRENT_BOT_VERSION] > 0 \
           and question_type_classifier \
           and intent_classifier \
           and intent_datas \
           and oos_intent_recognizer \
           and context_question_recognizer


def version_check(session_bot_version):
    return system_bot_version[CURRENT_BOT_VERSION] == session_bot_version


class VirtualHCMChatbot(object):
    def __init__(self, user):
        # For dialogue states tracking (list of dictionary(intent,types,action))
        self.user = user
        self.state_tracker = []
        self.report_able_states = []
        # self.state_tracker.append(State())
        # Answer generator
        self.answer_generator = AnswerGenerator()
        self.train_data = train_data_model

    def __regis_history(self, intent, question, answer, question_types, chat_type, context_question, action):
        state = State(intent, question, answer, question_types, chat_type, context_question, action)
        if action == chat_state.ANSWER:
            self.report_able_states.append(len(self.state_tracker))
        elif action == chat_state.CONFIRMATION_NG:
            # out of index exception not gonna happen but who knows
            bot_answer_idx = (len(self.state_tracker)-1)
            if bot_answer_idx >= 0:
                self.report_able_states.append(bot_answer_idx)

        self.state_tracker.append(state)

    def get_last_state(self):
        return self.state_tracker[len(self.state_tracker) - 1]

    def get_last_answer_ok_state(self):
        for state in reversed(self.state_tracker):
            if state.action == chat_state.ANSWER or state.action == chat_state.CONFIRMATION_OK:
                return state
        return None

    def get_last_report_able_state(self):
        if self.report_able_states:
            idx = self.report_able_states.pop()
            return self.state_tracker[idx], idx
        else:
            return None, None

    def report_able_states_to_db_data(self):
        if self.report_able_states:
            return COMMA.join([str(idx) for idx in self.report_able_states])
        else:
            return None

    def extract_reportable_states(self, indexes):
        if indexes:
            self.report_able_states = [int(idx) for idx in indexes.split(COMMA)]
        else:
            self.report_able_states = []

    def intent_reference_to_response_txt(self, intent):
        intent_reference = intent.references
        reference_info_to_message = []
        if len(intent_reference) == 1:
            for document_id in intent_reference:
                reference_info_to_message.append(self.__create_reference_info_message(None, document_id, intent_reference[document_id]))
        else:
            for idx, document_id in enumerate(intent_reference):
                reference_info_to_message.append(self.__create_reference_info_message(idx+1, document_id, intent_reference[document_id]))
        return MESSAGE_VIEW_REFERENCE.format(
            intent_name=intent.fullname,
            references=NEW_LINE.join(reference_info_to_message)
        )

    @staticmethod
    def __create_reference_info_message(idx, document_id, intent_reference):
        document = documents_data[document_id]
        link = ('Nguồn online: ' + document['link']) if document['link'] else ''
        page = ('Trang: ' + intent_reference['page']) if intent_reference['page'] else ''
        extra_info = ('Thông tin thêm: ' + intent_reference['extra_info']) if intent_reference['extra_info'] else ''
        reference_info = NEW_LINE.join([link, page, extra_info]).strip()
        author = 'Tác giả: ' + document['author'] + '\n' if reference_info else ''
        message = MESSAGE_REFERENCE_INFO.format(
            idx=(str(idx)+'.') if idx else '',
            reference_name=document['name'],
            reference_author=author,
            reference_info=reference_info
        )

        return message

    @staticmethod
    def __decide_action(chat_input, chat_type, intent, types, context_question, last_state):
        """Combines intent and question type recognition to decide bot action"""
        # print(last_state)
        if intent.intent_id == last_state.intent.intent_id and last_state.action == chat_state.AWAIT_CONFIRMATION:
            if chat_input.lower() == 'sai' \
                    or chat_input.lower() == 'sai rồi' \
                    or chat_input.lower() == 'khong'\
                    or chat_input.lower() == 'không'\
                    or chat_input.lower() == 'không phải':
                return chat_state.CONFIRMATION_NG
            elif chat_input.lower() == 'đúng'\
                    or chat_input.lower() == 'dung'\
                    or chat_input.lower() == 'đúng rồi'\
                    or chat_input.lower() == 'ừ'\
                    or chat_input.lower() == 'phải':
                return chat_state.CONFIRMATION_OK
            else:
                return chat_state.ERROR_COMMAND
        else:
            if (intent.intent_id and language_processor.analyze_sentence_components(intent, chat_input)) \
                    or chat_type == OUT_OF_SCOPE_DIALOGUE\
                    or not intent.intent_id \
                    or (intent.intent_id and context_question):
                return chat_state.ANSWER
            else:
                return chat_state.AWAIT_CONFIRMATION

    def chat(self, user_input=None, init=False):
        if not init:
            last_state = self.get_last_state()
            if last_state.action != chat_state.AWAIT_CONFIRMATION:
                # Input preprocesing
                segmented_input = language_processor.text_prepare(user_input, lower=True)
                # Predict
                hcm_question = oos_intent_recognizer.predict(segmented_input) == HCM_QUESTION
                context_question = context_question_recognizer.predict(segmented_input) == CONTEXT_QUESTION
                if hcm_question:
                    if context_question:
                        intent = last_state.intent
                    else:
                        intent_name = intent_classifier.predict(segmented_input)
                        intent = intent_datas[intent_name]
                    types = question_type_classifier.predict(segmented_input)
                    types = [int(t) for t in types]
                else:
                    # User asking out of scope question
                    intent = Intent()
                    types = []
            else:
                # If bot awaiting user confirmation so no need to predict
                hcm_question = True
                context_question = last_state.context_question
                intent = last_state.intent
                types = last_state.question_types
            # Decide what to do base on predicted data
            action = self.__decide_action(user_input, hcm_question, intent, types, context_question, last_state)
            bot_response = self.answer_generator.get_response(hcm_question, intent, types, action, last_state)
            self.__regis_history(intent, user_input, bot_response, types, hcm_question, context_question, action)
        else:
            bot_response = MESSAGE_BOT_GREATING
            self.__regis_history(Intent(), None, bot_response, [], False, False, chat_state.INITIAL)
        return bot_response


class AnswerGenerator:
    def __init__(self):
        self.question_id2type = QUESTION_TYPES_IDX2T
        self.question_type2id = QUESTION_TYPES_T2IDX

    def get_response(self, hcm_question, intent, types, action, last_state):
        if hcm_question:
            if action == chat_state.ANSWER:
                return self.__answer(intent, types)
            elif action == chat_state.AWAIT_CONFIRMATION:
                return self.__confirmation(intent)
            elif action == chat_state.CONFIRMATION_OK:
                return self.__answer(last_state.intent, last_state.question_types)
            elif action == chat_state.CONFIRMATION_NG:
                return self.__confirmation_ng()
            elif action == chat_state.ERROR_COMMAND:
                return self.__user_input_unknow_command()
        else:
            return self.__out_of_scope_response()

    @staticmethod
    def __confirmation(intent):
        return MESSAGE_CONFIRMATION.format(intent=intent.fullname)

    @staticmethod
    def __confirmation_ng():
        return MESSAGE_CHOOSE_TO_CONTRIBUTE

    def __answer(self, intent, types):
        if intent.intent_id:
            response = intent.base_response
            # Get type data exists in intent
            existing_types = [t for t in types if t in intent.corresponding_datas]
            # If any of user asking data types not exist in intent so just print all intent data
            if not existing_types:
                response += (SPACE + SPACE.join(random.choice(intent.corresponding_datas[key]) for key in intent.corresponding_datas))
            else:
                response += (SPACE + SPACE.join(random.choice(intent.corresponding_datas[key]) for key in existing_types))
        else:
            response = self.__nothing_to_response()
        return response

    @staticmethod
    def __out_of_scope_response():
        return MESSAGE_OOS_ANSWER

    @staticmethod
    def __nothing_to_response():
        return MESSAGE_NOTHING_TO_ANSWER

    @staticmethod
    def __user_input_unknow_command():
        return MESSAGE_USER_INPUT_UNKNOW_COMMAND


# For clearing GPU memory in case of load models failed
# but this is not working with tensorflow 2 anymore

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
