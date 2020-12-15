from pathlib import Path

# Global variables
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
# Special characters
HASH = '#'
PERIOD = '.'
COLON = ':'
COMMA = ','
PLUS = '+'
MINUS = '-'
SPACE = ' '
UNDERSCORE = '_'
EXCLAMATION = '!'
NEW_LINE = '\n'
# Encoding
UTF8 = 'utf-8'
UTF16 = 'utf-16'
# System
ACCESS_TOKEN = 'accesstoken'
# Websocket
TRAIN_CLASSIFIER_ROOM_GROUP = 'ws_train_classifier'
CHAT_ROOM_GROUP = 'ws_chat_'
# Other
IDX2OBJ = 'idx2obj'
OBJ2IDX = 'obj2idx'
# NLP
BERT = 'bert'
INTENT = 'intent'
QUESTION = 'question'
INTENT_DATA_FILE_NAME = 'intent_data.csv'
REFERENCES_FILE_NAME = 'references.json'
SYNONYMS_FILE_NAME = 'synonyms.json'
TRAIN_DATA_FILE_NAME = 'train_data.pickle'
TRAIN_DATA_FOLDER = 'extras/nlp/data/train_data/'
MODEL_DATA_FOLDER = 'extras/nlp/classifiers/trained/'
INTENT_MODEL_NAME = 'intent/model_weights'
INTENT_MODEL_CONFIG = 'extras/nlp/classifiers/trained/intent_config.json'
QUESTION_TYPE_MODEL_NAME = 'question_type/model_weights'
QUESTION_TYPE_MODEL_CONFIG = 'extras/nlp/classifiers/trained/question_type_config.json'
INTENT_MAP_FILE_PATH = 'extras/nlp/classifiers/trained/intent_map.json'
QUESTION_TYPE_MAP_FILE_PATH = 'extras/nlp/classifiers/trained/question_type_map.json'
DIALOGUE_INTENT_RECOGNIZER_FILE_PATH = 'extras/nlp/classifiers/trained/dialogue_intent_recognizer.pickle'
DIALOGUE_TFIDF_VECTORIZER_FILE_PATH = 'extras/nlp/classifiers/trained/dialogue_tfidf_vectorizer.pickle'
CONTEXT_QUESTION_RECOGNIZER_FILE_PATH = 'extras/nlp/classifiers/trained/context_question_recognizer.pickle'
CONTEXT_TFIDF_VECTORIZER_FILE_PATH = 'extras/nlp/classifiers/trained/context_tfidf_vectorizer.pickle'
CLASSIFIER_MODEL_FILES = ['checkpoint', 'model_weights.data-00000-of-00001', 'model_weights.index']
CLASSIFIER_TYPES = {
    INTENT: 1,
    QUESTION: 2
}
QUESTION_TYPE_MAP = {
    1: "what",
    2: "when",
    3: "where",
    4: "who",
    5: "why",
    6: "how",
    7: "yesno"
}
BOT_VERSION_FILE_PATH = 'extras/nlp/classifiers/trained/bot_version'
RESET_PASSWORD_MAIL_TEMPLATE = 'extras/data/email/reset_password_template.txt'
EMAIL_REGEX = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"


# Date format
class DateFormat(object):
    def __init__(self, format, regex):
        self.format = format
        self.regex = regex


DATETIME_DDMMYYYY = DateFormat('DD/MM/YYYY', '%d/%m/%Y')
DATETIME_DDMMYYYY_HHMMSS = DateFormat('DD/MM/YYYY HH:MM:SS', '%d/%m/%Y %H:%M:%S')
DATETIME_DJANGO_DEFUALT_DDMMYYYY = DateFormat('YYYY-MM-DD', '%Y-%m-%d')
DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS = DateFormat('YYYY-MM-DD', '%Y-%m-%dT%H:%M:%S.%f')
