from rest_framework.decorators import api_view
from rest_framework.response import Response
import vhcm.models.system_settings as setting_model
from vhcm.common.response_json import ResponseJSON
from vhcm.common.singleton import Singleton
from vhcm.common.dao.model_query import is_table_exists
from vhcm.common.utils.CH import isInt, isFloat
from vhcm.biz.authentication.user_session import ensure_admin
from vhcm.common.utils.crypto import decrypt


class ConfigLoader(object, metaclass=Singleton):
    def __init__(self):
        self.settings = None
        # Only load setting when project did its first migration
        if is_table_exists('system_settings'):
            self.settings = {}
            for setting in setting_model.SystemSetting.objects.all():
                if setting.setting_id in ENCRYPT_SETTING:
                    if setting.value:
                        value = decrypt(setting.value)
                    else:
                        value = None
                else:
                    value = setting.value
                self.settings[setting.setting_id] = {
                    setting_model.VALUE: value,
                    setting_model.DEFAULT: setting.default
                }

    def get_setting_value(self, key):
        setting = self.settings.get(key)
        if setting is None:
            raise KeyError('Setting not found: ', key)

        if setting[setting_model.VALUE]:
            return setting[setting_model.VALUE]
        else:
            return setting[setting_model.DEFAULT]

    def get_setting_value_array(self, key, separator):
        setting = self.settings.get(key)
        if setting is None:
            raise KeyError('Setting not found: ', key)
        if setting[setting_model.VALUE]:
            value = setting[setting_model.VALUE]
        else:
            if setting[setting_model.DEFAULT]:
                value = setting[setting_model.DEFAULT]
            else:
                return []

        return [v.strip() for v in value.split(separator) if v.strip()]

    def get_setting_value_int(self, key):
        setting = self.settings.get(key)
        if setting is None:
            raise KeyError('Setting not found: ', key)
        value = setting[setting_model.VALUE]
        if value and isInt(value):
            value = int(value)
        else:
            value = int(setting[setting_model.DEFAULT])

        return value

    def get_setting_value_float(self, key):
        setting = self.settings.get(key)
        if setting is None:
            raise KeyError('Setting not found: ', key)
        value = setting[setting_model.VALUE]
        if value and isFloat(value):
            value = float(value)
        else:
            value = float(setting[setting_model.DEFAULT])

        return value

    def get_setting(self, key):
        return setting_model.SystemSetting.objects.filter(setting_id=key).first()


# ALL CONFIGS
# Setting types
SYSTEM = 'system'
NLP = 'nlp'
REVIEW_PROCESS = 'review_process'
SETTING_TYPES = {
    SYSTEM: 1,
    NLP: 2,
    REVIEW_PROCESS: 3
}
# System
LOGIN_EXPIRATION_LIMIT = 'login_expiration_limit'
ACCEPT_IMAGE_FORMAT = 'accept_image_format'
DEFAULT_PASSWORD = 'default_password'
SYSTEM_MAIL = 'system_mail'
SYSTEM_MAIL_PASSWORD = 'system_mail_password'
RESET_PASSWORD_EXPIRE_TIME = 'reset_password_expire_time'
# NLP
VNCORENLP = 'vncorenlp'
STOPWORDS = 'stopwords'
CLASSIFIER_TRAINER_SCRIPT = 'classifier_train_script'
NAMED_ENTITY_TYPES = 'named_entity_types'
CRITICAL_DATA_NG_PATTERNS = 'subject_data_ng_pattern'
EXCLUDE_POS_TAG = 'exclude_pos_tag'
EXCLUDE_WORDS = 'exclude_word'
PREDICT_THRESHOLD = 'predict_threshold'
# Data review process
MAXIMUM_REJECT = 'maximum_reject'
MINIMUM_ACCEPT = 'minimum_accept'

# Settings need to encrypt before push to DB
ENCRYPT_SETTING = [
    SYSTEM_MAIL_PASSWORD
]

# Instance
config_loader = ConfigLoader()


@api_view(['GET'])
def add_system_settings(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    # Adding settings to DB
    settings = [
        (VNCORENLP,
         'Language processing: VNCoreNLP data path',
         'System path where VNCoreNLP files storing (absolute/relative path OK)',
         SETTING_TYPES[NLP],
         None,
         'extras/nlp/data/vncorenlp/VnCoreNLP-1.1.1.jar'),
        (CLASSIFIER_TRAINER_SCRIPT,
         'Language processing: Classifiers trainer script path',
         'System path where intent classifier trainer script file storing (absolute/relative path OK)',
         SETTING_TYPES[NLP],
         None,
         'extras/nlp/vhcm_trainer.py'),
        (EXCLUDE_POS_TAG,
         'Language processing: Exclude POS-tag',
         'These POS-tag will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         SETTING_TYPES[NLP],
         'E,A,L,CH,X',
         None),
        (NAMED_ENTITY_TYPES,
         'Language processing: Names entity types',
         'Accepted NER types for extracting main subjects in sentence',
         SETTING_TYPES[NLP],
         'LOC,PER,ORG,MISC',
         None),
        ('subject_data_ng_pattern',
         'Language processing: Bad subject structure patterns',
         'Using this to analyze main subjects in sentences is matching.\nInput pattern examples:\nX-main\nmain-X\nX-main-X\nIn that (main) is main subject, (X) is word types adjacent to main subject',
         SETTING_TYPES[NLP],
         'N-E-main,N-main',
         None),
        (EXCLUDE_WORDS,
         'Language processing: Exclude words',
         'These words will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         SETTING_TYPES[NLP],
         'bị,được,giữa,và,là',
         None),
        (STOPWORDS,
         'Language processing: Stopwords',
         'Words will be excluded from sentence during text preprocessing (absolute/relative path OK)',
         SETTING_TYPES[NLP],
         None,
         'extras/nlp/data/stopwords.txt'),
        (LOGIN_EXPIRATION_LIMIT,
         'System: Login expiration time',
         'Specify login expiration time threshold (in minutes)',
         SETTING_TYPES[SYSTEM],
         '5',
         '30'),
        (ACCEPT_IMAGE_FORMAT,
         'System: Acceptable image file format ',
         'Specify image file format that can be uploaded to system.\nSee available types at: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html',
         SETTING_TYPES[SYSTEM],
         'JPEG,JPEG 2000,PNG',
         None),
        (DEFAULT_PASSWORD,
         'System: New user default password',
         'Default password for newly created user',
         SETTING_TYPES[SYSTEM],
         None,
         '123'),
        (PREDICT_THRESHOLD,
         'Language processing: Predict threshold value (For question types predicting)',
         'Predict label as positive when predicted value >= threshold value',
         SETTING_TYPES[NLP],
         '0.75',
         '0.5'),
        (MAXIMUM_REJECT,
         'Knowledge data processing: Maximum rejects count',
         'Knowledge data can only be considered as approvable when rejects count below this value threshold',
         SETTING_TYPES[REVIEW_PROCESS],
         None,
         '3'),
        (MINIMUM_ACCEPT,
         'Knowledge data processing: Minimum accepts count',
         'Knowledge data will be approved when accepts count reach this value threshold',
         SETTING_TYPES[REVIEW_PROCESS],
         None,
         '5'),
        (SYSTEM_MAIL,
         'System: System email address',
         'Email address using to send mail from the system',
         SETTING_TYPES[SYSTEM],
         None,
         None),
        (SYSTEM_MAIL_PASSWORD,
         'System: System email password',
         'Password for the email using to send mail from the system',
         SETTING_TYPES[SYSTEM],
         None,
         None),
        (RESET_PASSWORD_EXPIRE_TIME,
         'System: Reset password session expire time',
         'Define how long user reset password session will live (in minute)',
         SETTING_TYPES[SYSTEM],
         None,
         '15'),
    ]

    settings = [setting_model.SystemSetting(setting_id=s[0], setting_name=s[1], description=s[2], type=s[3], value=s[4], default=s[5])
                for s in settings]
    setting_model.SystemSetting.objects.all().delete()
    setting_model.SystemSetting.objects.bulk_create(settings)

    result.set_status(True)
    result.set_result_data(True)
    response.data = result.to_json()
    return response
