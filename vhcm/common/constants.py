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
TRAIN_CLASSIFIER_ROOM_GROUP = '_train_classifier'
# Other
IDX2OBJ = 'idx2obj'
OBJ2IDX = 'obj2idx'
# NLP
BERT = 'bert'
INTENT = 'intent'
QUESTION = 'question'
TRAIN_DATA_FOLDER = 'extras/nlp/data/train_data/'
MODEL_DATA_FOLDER = 'extras/nlp/classifier/trained/'
INTENT_MODEL_NAME = 'intent/model_weights'
INTENT_MODEL_CONFIG = 'extras/nlp/classifier/trained/intent.config'
QUESTION_TYPE_MODEL_NAME = 'question_type/model_weights'
QUESTION_TYPE_MODEL_CONFIG = 'extras/nlp/classifier/trained/question_type.config'
INTENT_MAP_FILE_PATH = 'extras/nlp/classifier/trained/intent_map.pickle'
QUESTION_TYPE_MAP_FILE_PATH = 'extras/nlp/classifier/trained/question_type_map.pickle'
CLASSIFIER_TYPES = {
    INTENT: 1,
    QUESTION: 2
}
QUESTION_TYPE_MAP_PREDEFINE = 'question_type_map'


# Date format
class DateFormat(object):
    def __init__(self, format, regex):
        self.format = format
        self.regex = regex


DATETIME_DDMMYYYY = DateFormat('DD/MM/YYYY', '%d/%m/%Y')
DATETIME_DDMMYYYY_HHMMSS = DateFormat('DD/MM/YYYY HH:MM:SS', '%d/%m/%Y %H:%M:%S')
DATETIME_DJANGO_DEFUALT = DateFormat('YYYY-MM-DD', '%Y-%m-%d')
