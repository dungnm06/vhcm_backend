import json
import pandas as pd
from collections import namedtuple
import vhcm.models.knowledge_data_subject as subject_model
# import vhcm.models.knowledge_data_question as question_model
# import vhcm.models.knowledge_data_generated_question as generated_question_model
# import vhcm.models.knowledge_data_response_data as response_model
from vhcm.common.dao.native_query import execute_native_query
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


class Intent:
    def __init__(self, intent_id=0, intent=None, fullname=None,
                 raw_data=None, base_response=None,
                 corresponding_datas=None, subjects=None,
                 sentence_components=None, synonym_sets=None, references=None):
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
        if synonym_sets is None:
            synonym_sets = {}
        if references is None:
            references = []
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
        self.synonym_sets = synonym_sets
        self.references = references


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
        # # Questions
        # questions = question_model.Question.objects.filter(knowledge_data=knowledge_data)
        # for q in questions:
        #     # Generated questions
        #     generated_questions = generated_question_model.GeneratedQuestion.objects.filter(accept_status=True,
        #                                                                                     question=q)
        #     question = Question(q.question, [gq.generated_question for gq in generated_questions])
        #     intent.questions.append(question)
        # Raw data
        intent.raw_data = knowledge_data.raw_data
        # Base response
        intent.base_response = knowledge_data.base_response
        # # Response datas
        # response_datas = response_model.ResponseData.objects.filter(knowledge_data=knowledge_data)
        # for response in response_datas:
        #     intent.corresponding_datas[response.type] = response.answer
        #     # Intent types
        #     intent.intent_types.append(response.type)

        # Subjects
        subjects = subject_model.Subject.objects.filter(knowledge_data=knowledge_data)
        for subject in subjects:
            pass
            # Subject

            # Verbs
            # verbs = verbs_model.Verb.objects.filter(subject=subject)
            # intent.subjects.append(None)
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


def load_from_data_file(intents_data_path, references_path, synonyms_path):
    with open(synonyms_path, encoding=UTF8) as synonym_file, open(references_path, encoding=UTF8) as references_file:
        intent_maps = {}
        intent_datas = pd.read_csv(intents_data_path)
        references = json.load(references_file)
        synonyms = json.load(synonym_file)

        for idx, data in intent_datas.iterrows():
            intent = Intent()
            # ID
            intent.intent_id = data[INTENT_ID]

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
            sc = data[INTENT_VERBS]
            if not pd.isnull(cd) and not pd.isnull(sc):
                for cdi, sci in zip(cd.split(HASH), sc.split(HASH)):
                    split_idx = cdi.find(COLON)
                    intent.subjects.append({
                        'type': cdi[:split_idx],
                        'words': cdi[(split_idx + 1):],
                        'verbs': sci
                    })
            # # Sentence components
            # if not pd.isnull(sc):
            #     sc = sc.split(HASH)
            #     sentence_components = []
            #     for c in sc:
            #         if c == 'empty':
            #             sentence_components.append([])
            #         else:
            #             sentence_components.append(
            #                 [(c1.split(COLON)[0], c1.split(COLON)[1]) for c1 in c.split(PLUS)])
            #     # print(sentence_components)
            #     intent.sentence_components = sentence_components

            # Reference document
            rdi = references[str(data[INTENT_ID])]
            if rdi:
                intent.references = rdi

            # Synonym words dictionary
            synonym_ids = data[INTENT_SYNONYM_IDS]
            if synonym_ids:
                synonym_ids = synonym_ids.split(COMMA)
                for s in synonym_ids:
                    synonym_set = SynonymSet()
                    synonym_set.id = int(s)
                    synonym_set.meaning = synonyms[s][SYNONYM_MEANING]
                    synonym_set.words = synonyms[s][SYNONYM_WORDS]
                    intent.synonym_sets[s] = synonym_set
            # Push to intents map
            intent_maps[intent.intent] = intent

    return intent_maps

