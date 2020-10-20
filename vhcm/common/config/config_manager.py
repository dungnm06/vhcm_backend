from rest_framework.decorators import api_view
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

    def get_setting(self, key):
        return self.settings.filter(setting_id=key).first()


# ALL CONFIGS
VNCORENLP = 'vncorenlp'
NAMED_ENTITY_TYPES = 'named_entity_types'
CRITICAL_DATA_NG_PATTERNS = 'subject_data_ng_pattern'
EXCLUDE_POS_TAG = 'exclude_pos_tag'
EXCLUDE_WORDS = 'exclude_word'

# Instance
SYSTEM_SETTINGS = SystemSetting.objects.all()
CONFIG_LOADER = ConfigLoader(SYSTEM_SETTINGS)


@api_view(['GET'])
def add_system_settings(request):
    response = Response()
    result = ResponseJSON()

    # Adding settings to DB
    settings = [
        ('vncorenlp',
         'Language Processing: VNCoreNLP data path',
         'System path where VNCoreNLP files storing (absolute/relative path OK)',
         '',
         'data/nlu/vncorenlp/VnCoreNLP-1.1.1.jar'),
        ('exclude_pos_tag',
         'Language Processing: Exclude POS-tag',
         'These POS-tag will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         'E,A,L,CH,X',
         ''),
        ('named_entity_types',
         'Language Processing: Names entity types',
         'Accepted NER types for extracting main subjects in sentence',
         'LOC,PER,ORG,MISC',
         ''),
        ('subject_data_ng_pattern',
         'Language Processing: Bad subject structure patterns',
         'Using this to analyze main subjects in sentences is matching.\nInput pattern examples:\nX-main\nmain-X\nX-main-X\nIn that (main) is main subject, (X) is word types adjacent to main subject',
         'N-E-main,N-main',
         ''),
        ('exclude_word',
         'Language Processing: Exclude words',
         'These words will be ignored when analyze sentence subjects and verbs in language processing phase (comma separated)',
         'bị,được,giữa,và,là',
         '')
    ]

    settings = [SystemSetting(setting_id=s[0], setting_name=s[1], description=s[2], value=s[3], default=s[4]) for s in
                settings]
    SystemSetting.objects.all().delete()
    SystemSetting.objects.bulk_create(settings)

    result.set_status(True)
    result.set_result_data(True)
    response.data = result.to_json()
    return response
