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
# Encoding
UTF8 = 'utf-8'
UTF16 = 'utf-16'
# System
ACCESS_TOKEN = 'accesstoken'
# Websocket
WEBSOCKET_ROOM = 'ws'
INTENT_CLASSIFIER_ROOM_GROUP = '_intent_classifier'
QUESTION_CLASSIFIER_ROOM_GROUP = '_question_classifier'
# Other
IDX2OBJ = 'idx2obj'
OBJ2IDX = 'obj2idx'
# NLP
BERT = 'bert'
INTENT = 'intent'
QUESTION = 'question'
CLASSIFIER_TYPES = {
    INTENT: 1,
    QUESTION: 2
}
QUESTION_TYPE_DATA_PATH = 'question_type_data_path'
QUESTION_TYPE_MODEL_PATH = 'question_type_model_weights'
QUESTION_TYPE_MAP_FILE_PATH = 'question_type_map_file_path'
QUESTION_TYPE_MAP_PREDEFINE = 'question_type_map'
INTENT_DATA_PATH = 'intent_data_path'
INTENT_MODEL_PATH = 'intent_model_weights'
INTENT_MAP_FILE_PATH = 'intent_map_file_path'
SYNONYMS_FILE_PATH = 'synonyms_file_path'
GLOBAL_SYNONYMS_FILE_PATH = 'global_synonyms_file_path'
PREDICT_THRESHOLD = 'predict_threshold'
MAX_SENTENCE_LENGTH = 'max_sentence_length'


# Date format
class DateFormat(object):
    def __init__(self, format, regex):
        self.format = format
        self.regex = regex


DATETIME_DDMMYYYY = DateFormat('DD/MM/YYYY', '%d/%m/%Y')
DATETIME_DDMMYYYY_HHMMSS = DateFormat('DD/MM/YYYY HH:MM:SS', '%d/%m/%Y %H:%M:%S')
DATETIME_DJANGO_DEFUALT = DateFormat('YYYY-MM-DD', '%Y-%m-%d')
