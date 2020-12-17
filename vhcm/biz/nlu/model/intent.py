import json
import pandas as pd
from collections import namedtuple
# import vhcm.models.knowledge_data_subject as subject_model
# import vhcm.models.knowledge_data_question as question_model
# import vhcm.models.knowledge_data_generated_question as generated_question_model
# import vhcm.models.knowledge_data_response_data as response_model
# from vhcm.common.dao.native_query import execute_native_query
from vhcm.common.constants import *
from vhcm.biz.nlu.model.synonym import *

# Mapping
INTENT_ID = 'ID'
INTENT_NAME = 'Intent'
INTENT_FULL_NAME = 'IntentFullName'
# INTENT_QUESTIONS = 'Questions'
INTENT_RAW_DATA = 'Raw data'
INTENT_BASE_RESPONSE = 'BaseResponse'
# INTENT_INTENT_TYPES = 'IntentType'
INTENT_RESPONSE_ANSWERS = 'ResponseAnswers'
INTENT_SUBJECTS = 'Subjects'
INTENT_REFERENCES = 'ReferenceDocuments'
INTENT_VERBS = 'Verbs'
INTENT_SYNONYM_IDS = 'SynonymsID'

# Intent data columns
INTENT_DATA_COLUMNS = [INTENT_ID, INTENT_NAME, INTENT_FULL_NAME, INTENT_RAW_DATA, INTENT_BASE_RESPONSE,
                       INTENT_RESPONSE_ANSWERS, INTENT_SUBJECTS, INTENT_VERBS, INTENT_SYNONYM_IDS]

# Named tuple
Question = namedtuple('Question', ['question', 'generated_questions'])

# SQL
KNOWLEDGE_DATA_GET_SYNONYMS = '''
    SELECT
        kdsl.word,
        s.synonym_id,
        s.meaning,
        s.words
    FROM vhcm.knowledge_data kd
    INNER JOIN vhcm.knowledge_data_synonym_link kdsl
    ON kd.knowledge_data_id = kdsl.knowledge_data_id
    INNER JOIN vhcm.synonyms s
    ON s.synonym_id = kdsl.synonym_id
    WHERE kd.knowledge_data_id = %d;
'''

# Constants
INTENT_SUBJECT_TYPE = 'type'
INTENT_SUBJECT_WORDS = 'words'
INTENT_SUBJECT_VERBS = 'verbs'
INTENT_VERB_EMPTY = 'empty'


class Intent:
    def __init__(self, intent_id=0, intent=None, fullname=None,
                 raw_data=None, base_response=None,
                 corresponding_datas=None, subjects=None,
                 sentence_components=None, synonyms=None, ne_synonyms=None, references=None):
        # Default argument value is mutable
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil
        # if intent_types is None:
        #     intent_types = []
        if sentence_components is None:
            sentence_components = []
        if subjects is None:
            subjects = []
        if corresponding_datas is None:
            corresponding_datas = {}
        # if questions is None:
        #     questions = []
        if synonyms is None:
            synonyms = {}
        if ne_synonyms is None:
            ne_synonyms = {}
        if references is None:
            references = {}
        # Assign attributes
        self.intent_id = intent_id
        self.intent = intent
        self.fullname = fullname
        # self.questions = questions
        self.raw_data = raw_data
        self.base_response = base_response
        # self.intent_types = intent_types
        self.corresponding_datas = corresponding_datas
        self.subjects = subjects
        self.synonyms = synonyms
        self.ne_synonyms = ne_synonyms
        self.references = references


def load_from_data_file(intents_data_path, references_path, synonyms_path):
    with open(synonyms_path, encoding=UTF8) as synonym_file, open(references_path, encoding=UTF8) as references_file:
        intent_maps = {}
        intent_datas = pd.read_csv(intents_data_path, dtype=str)
        references = json.load(references_file)
        synonyms = json.load(synonym_file)

        reference_documents = references['documents']
        # Intent data
        for idx, data in intent_datas.iterrows():
            intent = Intent()
            # ID
            intent.intent_id = int(data[INTENT_ID])

            # Intent name
            intent.intent = data[INTENT_NAME]

            # Intent full name
            intent.fullname = data[INTENT_FULL_NAME]

            # # Questions
            # intent.questions = [q.strip() for q in data[INTENT_QUESTIONS].split(HASH)]

            # Raw data
            intent.raw_data = data[INTENT_RAW_DATA]

            # Base response
            intent.base_response = data[INTENT_BASE_RESPONSE]

            # # Intent types
            # intent.intent_types = [int(t) for t in data[INTENT_INTENT_TYPES].split(COMMA)]

            # Corresponding answers
            cd = data[INTENT_RESPONSE_ANSWERS].split(HASH)
            for answer in cd:
                type, answer = answer.split(UNDERSCORE)
                type = int(type)
                if type not in intent.corresponding_datas:
                    intent.corresponding_datas[type] = []
                intent.corresponding_datas[type].append(answer)

            # Subjects (Critical datas)
            cd = data[INTENT_SUBJECTS]
            verbs = data[INTENT_VERBS]
            if not pd.isnull(cd) and not pd.isnull(verbs):
                for cdi, verb in zip(cd.split(HASH), verbs.split(HASH)):
                    split_idx = cdi.find(COLON)
                    if verb == INTENT_VERB_EMPTY:
                        verb = []
                    else:
                        verb = [(v.split(COLON)[0], v.split(COLON)[1]) for v in verb.split(PLUS)]
                    intent.subjects.append({
                        INTENT_SUBJECT_TYPE: cdi[:split_idx],
                        INTENT_SUBJECT_WORDS: cdi[(split_idx + 1):],
                        INTENT_SUBJECT_VERBS: verb
                    })

            # Reference document
            intent.references = references['intent_references'].get(str(data[INTENT_ID]))

            # Synonym words dictionary
            synonym_ids = data[INTENT_SYNONYM_IDS]
            if not pd.isnull(synonym_ids):
                synonym_ids = synonym_ids.split(COMMA)
                for s in synonym_ids:
                    synonym_set = SynonymSet()
                    synonym_set.id = int(s)
                    synonym_set.meaning = synonyms[s][SYNONYM_MEANING]
                    synonym_set.words = synonyms[s][SYNONYM_WORDS]
                    intent.synonyms[s] = synonym_set
            # Push to intents map
            intent_maps[intent.intent] = intent

    return intent_maps, reference_documents
