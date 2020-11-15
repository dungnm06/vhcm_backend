from collections import namedtuple
from .synonym import SynonymSet
import vhcm.models.knowledge_data_subject as subject_model
import vhcm.models.knowledge_data_verbs as verbs_model
import vhcm.models.knowledge_data_question as question_model
import vhcm.models.knowledge_data_generated_question as generated_question_model
import vhcm.models.knowledge_data_response_data as response_model
from vhcm.common.dao.native_query import execute_native_query
from vhcm.common.constants import *

# Mapping
INTENT_ID = 'ID'
INTENT_NAME = 'Intent'
INTENT_FULL_NAME = 'IntentFullName'
INTENT_QUESTIONS = 'Questions'
INTENT_RAW_DATA = 'Raw data'
INTENT_BASE_RESPONSE = 'BaseResponse'
INTENT_INTENT_TYPES = 'IntentType'
INTENT_CORRESPONDING_DATAS = 'Corresponding Data'
INTENT_CRITICAL_DATAS = 'CriticalData'
INTENT_REFERENCE_DOC_ID = 'Reference Document ID'
INTENT_REFERENCE_DOC_PAGE = 'Page'
INTENT_VERB_COMPONENTS = 'Verb Of Questions'
INTENT_SYNONYM_IDS = 'Synonyms ID'

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


class Intent:
    def __init__(self, intent_id=0, name='', fullname='', questions=None,
                 raw_data='', base_response='',
                 intent_types=None, corresponding_datas=None, subjects=None,
                 sentence_components=None, synonym_sets=None):
        # Default argument value is mutable
        # https://florimond.dev/blog/articles/2018/08/python-mutable-defaults-are-the-source-of-all-evil
        if intent_types is None:
            intent_types = []
        if sentence_components is None:
            sentence_components = []
        if subjects is None:
            subjects = []
        if corresponding_datas is None:
            corresponding_datas = {}
        if questions is None:
            questions = []
        if synonym_sets is None:
            synonym_sets = {}
        # Assign attributes
        self.intent_id = intent_id
        self.name = name
        self.fullname = fullname
        self.questions = questions
        self.raw_data = raw_data
        self.base_response = base_response
        self.intent_types = intent_types
        self.corresponding_datas = corresponding_datas
        self.subjects = subjects
        self.synonym_sets = synonym_sets


def load_from_db(models):
    intent_maps = {}
    for knowledge_data in models:
        intent = Intent()
        # ID
        intent.intent_id = knowledge_data.knowledge_data_id
        # Intent name
        intent.intent = knowledge_data.intent
        # Intent full name
        intent.name = knowledge_data.intent_fullname
        # Questions
        questions = question_model.Question.objects.filter(knowledge_data=knowledge_data)
        for q in questions:
            # Generated questions
            generated_questions = generated_question_model.GeneratedQuestion.objects.filter(accept_status=True,
                                                                                            question=q)
            question = Question(q.question, [gq.generated_question for gq in generated_questions])
            intent.questions.append(question)
        # Raw data
        intent.raw_data = knowledge_data.raw_data
        # Base response
        intent.base_response = knowledge_data.base_response
        # Response datas
        response_datas = response_model.ResponseData.objects.filter(knowledge_data=knowledge_data)
        for response in response_datas:
            intent.corresponding_datas[response.type] = response.answer
            # Intent types
            intent.intent_types.append(response.type)

        # Subjects
        subjects = subject_model.Subject.objects.filter(knowledge_data=knowledge_data)
        for subject in subjects:
            # Subject

            # Verbs
            verbs = verbs_model.Verb.objects.filter(subject=subject)
            intent.subjects.append(None)
        # Verbs

        # Synonym words dictionary
        synonyms = execute_native_query(KNOWLEDGE_DATA_GET_SYNONYMS, [knowledge_data.knowledge_data_id])
        for synonym in synonyms:
            synonym_set = SynonymSet()
            synonym_set.id = synonym.synonym_id
            synonym_set.meaning = synonym.meaning
            synonym_set.words = synonym.words.split(COMMA)
            intent.synonym_sets[synonym.synonym_id] = synonym_set
        # Push to intents map
        intent_maps[intent.intent] = intent

    return intent_maps
