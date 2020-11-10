from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from vhcm.models.system_settings import SystemSetting
from vhcm.common.response_json import ResponseJSON
from vhcm.common.singleton import Singleton


class ConfigLoader(object, metaclass=Singleton):
    def __init__(self, settings):
        self.settings = settings

    def get_setting_value(self, key):
        setting = self.settings.filter(setting_id=key).first()
        if setting is None:
            raise Exception('Setting not found: ', key)

        if setting.value:
            return setting.value
        else:
            return setting.default

    def get_setting_value_array(self, key, separator):
        setting = self.settings.filter(setting_id=key).first()
        if setting is None:
            raise Exception('Setting not found: ', key)
        value = None
        if setting.value:
            value = setting.value
        else:
            value = setting.default

        return [v.strip() for v in value.split(separator)]

    def get_setting_value_int(self, key):
        setting = self.settings.filter(setting_id=key).first()
        if setting is None:
            raise Exception('Setting not found: ', key)
        value = None
        if setting.value:
            value = setting.value
        else:
            value = setting.default

        return int(value)

    def get_setting_value_float(self, key):
        setting = self.settings.filter(setting_id=key).first()
        if setting is None:
            raise Exception('Setting not found: ', key)
        value = None
        if setting.value:
            value = setting.value
        else:
            value = setting.default

        return float(value)

    def get_setting(self, key):
        return self.settings.filter(setting_id=key).first()


# ALL CONFIGS
# Setting types
SYSTEM = 'system'
NLP = 'nlp'
SETTING_TYPES = {
    SYSTEM: 1,
    NLP: 2
}
# System
LOGIN_EXPIRATION_LIMIT = 'login_expiration_limit'
ACCEPT_IMAGE_FORMAT = 'accept_image_format'
DEFAULT_PASSWORD = 'default_password'
# TRAIN_DATA_FOLDER = 'train_data_folder'
# NLP
VNCORENLP = 'vncorenlp'
CLASSIFIER_TRAINER_SCRIPT = 'classifier_train_script'
NAMED_ENTITY_TYPES = 'named_entity_types'
CRITICAL_DATA_NG_PATTERNS = 'subject_data_ng_pattern'
EXCLUDE_POS_TAG = 'exclude_pos_tag'
EXCLUDE_WORDS = 'exclude_word'
PREDICT_THRESHOLD = 'predict_threshold'

# Instance
SYSTEM_SETTINGS = SystemSetting.objects.all()
CONFIG_LOADER = ConfigLoader(SYSTEM_SETTINGS)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def add_system_settings(request):
    response = Response()
    result = ResponseJSON()

    # Adding settings to DB
    settings = [
        ('vncorenlp',
         'Language Processing: VNCoreNLP data path',
         'System path where VNCoreNLP files storing (absolute/relative path OK)',
         SETTING_TYPES[NLP],
         '',
         'extras/nlp/data/vncorenlp/VnCoreNLP-1.1.1.jar'),
        ('classifier_train_script',
         'Language Processing: Classifiers trainer script path',
         'System path where intent classifier trainer script file storing (absolute/relative path OK)',
         SETTING_TYPES[NLP],
         '',
         'extras/nlp/vhcm_trainer.py'),
        ('exclude_pos_tag',
         'Language Processing: Exclude POS-tag',
         'These POS-tag will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         SETTING_TYPES[NLP],
         'E,A,L,CH,X',
         ''),
        ('named_entity_types',
         'Language Processing: Names entity types',
         'Accepted NER types for extracting main subjects in sentence',
         SETTING_TYPES[NLP],
         'LOC,PER,ORG,MISC',
         ''),
        ('subject_data_ng_pattern',
         'Language Processing: Bad subject structure patterns',
         'Using this to analyze main subjects in sentences is matching.\nInput pattern examples:\nX-main\nmain-X\nX-main-X\nIn that (main) is main subject, (X) is word types adjacent to main subject',
         SETTING_TYPES[NLP],
         'N-E-main,N-main',
         ''),
        ('exclude_word',
         'Language Processing: Exclude words',
         'These words will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         SETTING_TYPES[NLP],
         'bị,được,giữa,và,là',
         ''),
        ('login_expiration_limit',
         'System: Login expiration time',
         'Specify login expiration time threshold (in minutes)',
         SETTING_TYPES[SYSTEM],
         '5',
         '30'),
        ('accept_image_format',
         'System: Acceptable image file format ',
         'Specify image file format that can be uploaded to system.\nSee available types at: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html',
         SETTING_TYPES[SYSTEM],
         'JPEG,JPEG 2000,PNG',
         ''),
        ('default_password',
         'System: New user default password',
         'Default password for newly created user',
         SETTING_TYPES[SYSTEM],
         'vhcm-user',
         '123'),
        ('predict_threshold',
         'Language Processing: Predict threshold value (For question types predicting)',
         'Predict label as positive when predicted value >= threshold value',
         SETTING_TYPES[NLP],
         '0.75',
         '0.5'),
        # ('train_data_folder',
        #  'System: Train data folder path',
        #  'System path where train data files storing (absolute/relative path OK)',
        #  SETTING_TYPES[SYSTEM],
        #  '',
        #  'extras/nlp/data/train_data/'),
    ]

    settings = [SystemSetting(setting_id=s[0], setting_name=s[1], description=s[2], type=s[3], value=s[4], default=s[5]) for s in
                settings]
    SystemSetting.objects.all().delete()
    SystemSetting.objects.bulk_create(settings)

    result.set_status(True)
    result.set_result_data(True)
    response.data = result.to_json()
    return response
