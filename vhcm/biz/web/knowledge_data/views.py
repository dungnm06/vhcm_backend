from collections import Counter
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.db import transaction
from vhcm.common.dao.model_query import get_latest_id
from vhcm.common.response_json import ResponseJSON
import vhcm.models.knowledge_data as knowledge_data_model
import vhcm.models.knowledge_data_response_data as response_data_model
import vhcm.models.knowledge_data_subject as subject_model
import vhcm.models.reference_document as document_model
import vhcm.models.synonym as synonym_model
import vhcm.models.knowledge_data_reference_document_link as kd_document_model
import vhcm.models.knowledge_data_question as question_model
import vhcm.models.knowledge_data_synonym_link as kd_synonym_model
import vhcm.models.knowledge_data_generated_question as gq_model
from vhcm.biz.authentication.user_session import get_current_user, ensure_admin
from vhcm.common.constants import *
from vhcm.common.utils.CH import isInt
from .sql import GET_ALL_KNOWLEDGE_DATA, GET_ALL_TRAINABLE_KNOWLEDGE_DATA
from vhcm.common.dao.native_query import execute_native_query


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()

    query_data = execute_native_query(GET_ALL_KNOWLEDGE_DATA)
    result_data = {
        'knowledges': []
    }
    for data in query_data:
        knowledge_data = {
            'id': data.id,
            'intent': data.intent,
            'intent_fullname': data.intent_fullname,
            'status': knowledge_data_model.PROCESS_STATUS_DICT[data.status],
            'create_user': data.create_user,
            'create_user_id': data.create_user_id,
            'edit_user': data.edit_user,
            'edit_user_id': data.edit_user_id,
            'cdate': data.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'mdate': data.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        }
        result_data['knowledges'].append(knowledge_data)

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_trainable(request):
    response = Response()
    result = ResponseJSON()

    ensure_admin(request)

    query_data = execute_native_query(GET_ALL_TRAINABLE_KNOWLEDGE_DATA)
    result_data = {
        'knowledges': []
    }
    for data in query_data:
        knowledge_data = {
            'id': data.id,
            'intent': data.intent,
            'intent_fullname': data.intent_fullname,
            'status': knowledge_data_model.PROCESS_STATUS_DICT[data.status],
            'create_user': data.create_user,
            'create_user_id': data.create_user_id,
            'edit_user': data.edit_user,
            'edit_user_id': data.edit_user_id,
            'cdate': data.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'mdate': data.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        }
        result_data['knowledges'].append(knowledge_data)

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get(request):
    response = Response()
    result = ResponseJSON()

    try:
        intent = request.data[knowledge_data_model.INTENT] if request.method == 'POST' else request.GET[
            knowledge_data_model.INTENT]
    except KeyError:
        raise APIException('Can\'t get knowledge data infomations, missing intent id')

    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(intent=intent).first()
    if not knowledge_data:
        raise APIException('Invalid intent id, couldnt find knowledge data')

    # Response data
    response_datas = response_data_model.ResponseData.objects.filter(knowledge_data=knowledge_data)
    response_data_display = []
    for response_data in response_datas:
        response_data_display.append({
            'type': response_data_model.RESPONSE_TYPES_IDX2T[response_data.type],
            'answer': response_data.answer
        })

    # Subject
    subjects = subject_model.Subject.objects.filter(knowledge_data=knowledge_data)
    subjects_display = []
    for subject in subjects:
        # Words in subjects
        words = []
        for pair in subject.subject_data.split(PLUS):
            type_word_pair = pair.split(COLON)
            words.append({
                'type': type_word_pair[0],
                'word': type_word_pair[1]
            })
        # Verbs
        verb = []
        if subject.verbs:
            for pair in subject.verbs.split(PLUS):
                type_word_pair = pair.split(COLON)
                verb.append({
                    'type': type_word_pair[0],
                    'word': type_word_pair[1]
                })
        subjects_display.append({
            'type': subject.type,
            'word': words,
            'verb': verb
        })

    # Questions
    questions = question_model.Question.objects.filter(knowledge_data=knowledge_data)
    questions_display = []
    for question in questions:
        # Generated questions
        generated_questions = []
        generated_question_models = gq_model.GeneratedQuestion.objects.filter(question=question)
        for generated_question in generated_question_models:
            generated_questions.append({
                'question': generated_question.generated_question,
                'accept': 1 if generated_question.accept_status else 0
            })
        questions_display.append({
            'question': question.question,
            'generated_questions': generated_questions,
            'type': [int(t) for t in question.type.split(COMMA)]
        })

    # Synonyms
    synonym_links = kd_synonym_model.KnowledgeDataSynonymLink.objects.filter(knowledge_data=knowledge_data)
    synonyms_display = []
    tmp_dict = {}
    for synonym in synonym_links:
        if synonym.word not in tmp_dict:
            tmp_dict[synonym.word] = []
        tmp_dict[synonym.word].append({
            'id': synonym.synonym.synonym_id,
            'meaning': synonym.synonym.meaning,
            'words': synonym.synonym.words.split(COMMA)
        })
    for word in tmp_dict:
        synonyms_display.append({
            'word': word,
            'synonyms': tmp_dict[word]
        })

    # Reference Document
    document_links = kd_document_model.KnowledgeDataRefercenceDocumentLink.objects.filter(knowledge_data=knowledge_data)
    documents_display = []
    for document in document_links:
        documents_display.append({
            'id': document.reference_document.reference_document_id,
            'name': document.reference_document.reference_name,
            'page': document.page,
            'extra_info': document.extra_info
        })

    result_data = {
        'knowledge_data': {
            'id': knowledge_data.knowledge_data_id,
            'intent': knowledge_data.intent,
            'intentFullName': knowledge_data.intent_fullname,
            'baseResponse': knowledge_data.base_response,
            'coresponse': response_data_display,
            'criticalData': subjects_display,
            'documentReference': documents_display,
            'questions': questions_display,
            'rawData': knowledge_data.raw_data,
            'synonyms': synonyms_display,
            'status': knowledge_data_model.PROCESS_STATUS_DICT[knowledge_data.status],
            'create_user': knowledge_data.create_user.username,
            'create_user_id': knowledge_data.create_user.user_id,
            'edit_user': knowledge_data.edit_user.username,
            'edit_user_id': knowledge_data.edit_user.user_id,
            'cdate': knowledge_data.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'mdate': knowledge_data.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        }
    }

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
@transaction.atomic
def add(request):
    response = Response()
    result = ResponseJSON()

    errors = validate(request, 'add')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    # Add new Knowledge data
    knowledge_data = knowledge_data_model.KnowledgeData()

    # Intent
    knowledge_data.intent = request.data.get('intent').strip()
    # Intent fullname
    knowledge_data.intent_fullname = request.data.get('intentFullName').strip()
    # Base response
    knowledge_data.base_response = request.data.get('baseResponse').strip()
    # Raw data
    knowledge_data.raw_data = request.data.get('rawData').strip()
    # User
    user = get_current_user(request)
    knowledge_data.create_user = user
    knowledge_data.edit_user = user

    knowledge_data.save()

    # Reference document
    references = []
    next_reference_id = get_latest_id(kd_document_model.KnowledgeDataRefercenceDocumentLink, kd_document_model.ID)

    for i, reference in enumerate(request.data.get('documentReference')):
        try:
            document_id = int(reference['id'])
            document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
            if document is None:
                raise ValueError('')
            page = int(reference['page']) if reference['page'].strip() else None
            extra_info = reference['extra_info'].strip()
            references.append(kd_document_model.KnowledgeDataRefercenceDocumentLink(
                id=(next_reference_id + i),
                knowledge_data=knowledge_data,
                reference_document=document,
                page=page,
                extra_info=extra_info
            ))
        except ValueError:
            raise APIException('Reference document id is invalid ({})'.format(reference['id']))
    kd_document_model.KnowledgeDataRefercenceDocumentLink.objects.bulk_create(references)

    # Response data
    response_datas = []
    next_response_data_id = get_latest_id(response_data_model.ResponseData, response_data_model.ID)

    for i, rd in enumerate(request.data.get('coresponse')):
        response_datas.append(response_data_model.ResponseData(
            response_data_id=(next_response_data_id + i),
            knowledge_data=knowledge_data,
            type=response_data_model.RESPONSE_TYPES_T2IDX[rd['type'].lower()],
            answer=rd['answer']
        ))
    response_data_model.ResponseData.objects.bulk_create(response_datas)

    # Subjects
    subjects = []
    next_subject_id = get_latest_id(subject_model.Subject, subject_model.ID)

    for i, sj in enumerate(request.data.get('criticalData')):
        type = sj['type']
        subject_data = []
        for word in sj['word']:
            subject_data.append((word['type'], word['word']))
        # Eg: MISC:N:Thư+V:chúc_mừng+N:năm+R:mới
        # Eg2: LOC:N:làng+Np:Kim_Liên
        subject_data = PLUS.join([(s1[0] + COLON + s1[1]) for s1 in subject_data])

        # Verbs
        if not sj['verb']:
            verb = None
        else:
            verb = PLUS.join([(v['type'] + COLON + v['word']) for v in sj['verb']])

        subjects.append(subject_model.Subject(
            subject_id=(next_subject_id + i),
            knowledge_data=knowledge_data,
            type=type,
            subject_data=subject_data,
            verbs=verb
        ))
    subject_model.Subject.objects.bulk_create(subjects)

    # Questions
    questions = []
    generated_questions = []
    next_question_id = get_latest_id(question_model.Question, question_model.ID)
    next_g_question_id = get_latest_id(gq_model.GeneratedQuestion, gq_model.ID)

    for i, q in enumerate(request.data.get('questions')):
        questions.append(question_model.Question(
            question_id=(next_question_id + i),
            knowledge_data=knowledge_data,
            question=q['question'],
            type=COMMA.join([str(t) for t in q['type']])
        ))
        try:
            for i2, gqs in enumerate(q['generated_questions']):
                generated_question = gq_model.GeneratedQuestion(
                    generated_question_id=(next_g_question_id + i2),
                    generated_question=gqs['question'],
                    accept_status=gq_model.ACCEPT_STATUS[gqs['accept']],
                    question_id=(next_question_id + i)
                )
                generated_questions.append(generated_question)
            next_g_question_id += len(q['generated_questions'])
        except KeyError:
            raise APIException('Generated questions data is malformed')

    question_model.Question.objects.bulk_create(questions)
    gq_model.GeneratedQuestion.objects.bulk_create(generated_questions)

    # Synonyms
    kd_synonym_links = []
    next_synonym_link_id = get_latest_id(kd_synonym_model.KnowledgeDataSynonymLink, kd_synonym_model.ID)
    for synonym_word_pair in request.data.get('synonyms'):
        word = synonym_word_pair['word']
        for i, s_id in enumerate(synonym_word_pair['synonyms']):
            synonym = synonym_model.Synonym.objects.filter(synonym_id=s_id).first()
            if synonym is None:
                raise Exception('Invalid synonym group ids: {}'.format(s_id))
            # If word metion in data not in synonyms dictionary so add it
            syn_words = [s.lower() for s in synonym.words.split()]
            if word.lower() not in syn_words:
                syn_words.append(word)
                synonym.words = COMMA.join(syn_words)
                synonym.save()
            # Relation model regist
            kd_synonym_links.append(kd_synonym_model.KnowledgeDataSynonymLink(
                id=(next_synonym_link_id + i),
                knowledge_data=knowledge_data,
                synonym=synonym,
                word=word
            ))
        next_synonym_link_id += len(synonym_word_pair['synonyms'])
    kd_synonym_model.KnowledgeDataSynonymLink.objects.bulk_create(kd_synonym_links)

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['POST'])
@transaction.atomic
def edit(request):
    response = Response()
    result = ResponseJSON()

    errors = validate(request, 'edit')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    # Get existing Knowledge data
    kd_id = request.data.get('id')
    if not (kd_id and isInt(kd_id)):
        raise APIException('Invalid intent id: ID({})'.format(kd_id))

    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=kd_id).first()
    if knowledge_data is None:
        raise APIException('Intent id not found: ID({})'.format(kd_id))

    # Intent
    knowledge_data.intent = request.data.get('intent').strip()
    # Intent fullname
    knowledge_data.intent_fullname = request.data.get('intentFullName').strip()
    # Base response
    knowledge_data.base_response = request.data.get('baseResponse').strip()
    # Raw data
    knowledge_data.raw_data = request.data.get('rawData').strip()
    # User
    user = get_current_user(request)
    knowledge_data.edit_user = user

    knowledge_data.save()

    # Reference document
    kd_document_model.KnowledgeDataRefercenceDocumentLink.objects.filter(knowledge_data=knowledge_data).delete()
    references = []
    next_reference_id = get_latest_id(kd_document_model.KnowledgeDataRefercenceDocumentLink, kd_document_model.ID)

    for i, reference in enumerate(request.data.get('documentReference')):
        try:
            document_id = int(reference['id'])
            document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
            if document is None:
                raise ValueError('')
            page = int(reference['page']) if reference['page'].strip() else None
            extra_info = reference['extra_info'].strip()
            references.append(kd_document_model.KnowledgeDataRefercenceDocumentLink(
                id=(next_reference_id + i),
                knowledge_data=knowledge_data,
                reference_document=document,
                page=page,
                extra_info=extra_info
            ))
        except ValueError:
            raise APIException('Reference document id is invalid ({})'.format(reference['id']))
    kd_document_model.KnowledgeDataRefercenceDocumentLink.objects.bulk_create(references)

    # Response data
    response_data_model.ResponseData.objects.filter(knowledge_data=knowledge_data).delete()
    response_datas = []
    next_response_data_id = get_latest_id(response_data_model.ResponseData, response_data_model.ID)

    for i, rd in enumerate(request.data.get('coresponse')):
        response_datas.append(response_data_model.ResponseData(
            response_data_id=(next_response_data_id + i),
            knowledge_data=knowledge_data,
            type=response_data_model.RESPONSE_TYPES_T2IDX[rd['type'].lower()],
            answer=rd['answer']
        ))
    response_data_model.ResponseData.objects.bulk_create(response_datas)

    # Subjects
    subject_model.Subject.objects.filter(knowledge_data=knowledge_data).delete()
    subjects = []
    next_subject_id = get_latest_id(subject_model.Subject, subject_model.ID)

    for i, sj in enumerate(request.data.get('criticalData')):
        type = sj['type']
        subject_data = []
        for word in sj['word']:
            subject_data.append((word['type'], word['word']))
        # Eg: MISC:N:Thư+V:chúc_mừng+N:năm+R:mới
        # Eg2: LOC:N:làng+Np:Kim_Liên
        subject_data = PLUS.join([(s1[0] + COLON + s1[1]) for s1 in subject_data])

        # Verbs
        if not sj['verb']:
            verbs = None
        else:
            verbs = PLUS.join([(v['type'] + COLON + v['word']) for v in sj['verb']])

        subjects.append(subject_model.Subject(
            subject_id=(next_subject_id + i),
            knowledge_data=knowledge_data,
            type=type,
            subject_data=subject_data,
            verbs=verbs
        ))
    subject_model.Subject.objects.bulk_create(subjects)

    # Questions
    question_model.Question.objects.filter(knowledge_data=knowledge_data).delete()
    questions = []
    generated_questions = []
    next_question_id = get_latest_id(question_model.Question, question_model.ID)
    next_g_question_id = get_latest_id(gq_model.GeneratedQuestion, gq_model.ID)

    for i, q in enumerate(request.data.get('questions')):
        questions.append(question_model.Question(
            question_id=(next_question_id + i),
            knowledge_data=knowledge_data,
            question=q['question'],
            type=COMMA.join([str(t) for t in q['type']])
        ))
        try:
            for i2, gqs in enumerate(q['generated_questions']):
                generated_question = gq_model.GeneratedQuestion(
                    generated_question_id=(next_g_question_id + i2),
                    generated_question=gqs['question'],
                    accept_status=gq_model.ACCEPT_STATUS[gqs['accept']],
                    question_id=(next_question_id + i)
                )
                generated_questions.append(generated_question)
            next_g_question_id += len(q['generated_questions'])
        except KeyError:
            raise APIException('Generated questions data is malformed')

    question_model.Question.objects.bulk_create(questions)
    gq_model.GeneratedQuestion.objects.bulk_create(generated_questions)

    # Synonyms
    kd_synonym_model.KnowledgeDataSynonymLink.objects.filter(knowledge_data=knowledge_data).delete()
    kd_synonym_links = []
    next_synonym_link_id = get_latest_id(kd_synonym_model.KnowledgeDataSynonymLink, kd_synonym_model.ID)
    for synonym_word_pair in request.data.get('synonyms'):
        word = synonym_word_pair['word']
        for i, s_id in enumerate(synonym_word_pair['synonyms']):
            synonym = synonym_model.Synonym.objects.filter(synonym_id=s_id).first()
            if synonym is None:
                raise Exception('Invalid synonym group ids: {}'.format(s_id))
            # If word metion in data not in synonyms dictionary so add it
            syn_words = [s.lower() for s in synonym.words.split()]
            if word.lower() not in syn_words:
                syn_words.append(word)
                synonym.words = COMMA.join(syn_words)
                synonym.save()
            # Relation model regist
            kd_synonym_links.append(kd_synonym_model.KnowledgeDataSynonymLink(
                id=(next_synonym_link_id + i),
                knowledge_data=knowledge_data,
                synonym=synonym,
                word=word
            ))
        next_synonym_link_id += len(synonym_word_pair['synonyms'])
    kd_synonym_model.KnowledgeDataSynonymLink.objects.bulk_create(kd_synonym_links)

    result.set_status(True)
    response.data = result.to_json()
    return response


def validate(request, mode):
    errors = []

    # Intent
    if not ('intent' in request.data and request.data.get('intent').strip()):
        errors.append('Missing intent id')
    else:
        knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(
            intent__iexact=request.data.get('intent')).first()
        if knowledge_data is not None and mode == 'add':
            errors.append('Duplicated intent id')

    # Intent full name
    if not ('intentFullName' in request.data and request.data.get('intentFullName').strip()):
        errors.append('Missing intent name')

    # Base response
    if not ('baseResponse' in request.data and request.data.get('baseResponse')):
        errors.append('Missing base response')

    # Response data
    if not ('coresponse' in request.data and request.data.get('coresponse')):
        errors.append('Missing response data, response data must be at least one')
    else:
        err_rd_types = []
        type_check = []
        for i, rd in enumerate(request.data.get('coresponse')):
            type = rd['type'].lower()
            if type not in response_data_model.RESPONSE_TYPES_T2IDX:
                err_rd_types.append(rd['type'])
            if not rd['answer'].strip():
                errors.append('Response data #{} is empty'.format(i + 1))
            type_check.append(type)
        if err_rd_types:
            errors.append('Invalid response data type: {}'.format(', '.join(err_rd_types)))
        type_check = Counter(type_check)
        type_check = [k for k in type_check if type_check[k] > 1]
        if type_check:
            errors.append('Response data type duplicated: {}'.format(', '.join(type_check)))

    # Subjects
    if not ('criticalData' in request.data and request.data.get('criticalData')):
        errors.append('Missing subject data, must be at least one main subject')
    else:
        subjects = request.data.get('criticalData')
        for i, sj in enumerate(subjects):
            if sj['type'] not in subject_model.SUBJECT_TYPES:
                errors.append('Subject data #{} is invalid ({})'.format(i + 1, sj['type']))
            if not sj['word']:
                errors.append('Subject data #{} is empty'.format(i + 1))

    # Reference document
    if not ('documentReference' in request.data and request.data.get('documentReference')):
        errors.append('Knowledge data must belong to atleast one reference document')

    # Questions
    if not ('questions' in request.data
            and isinstance(request.data.get('questions'), list)
            and len(request.data.get('questions')) > 0):
        errors.append('Knowledge data must has atleast 1 question')
    else:
        for idx, question in enumerate(request.data.get('questions')):
            if not ('type' in question
                    and isinstance(question.get('type'), list)
                    and len(question.get('type')) > 0):
                errors.append('Question "{}", type not defined'.format(question.get('question', '#'+str(idx+1))))
            elif any([t not in question_model.QUESTION_TYPES_IDX2T for t in question.get('type')]):
                errors.append('Question "{}", unknow question type included'.format(question.get('question', '#'+str(idx+1))))

    # Raw data
    if not ('rawData' in request.data and request.data.get('rawData').strip()):
        errors.append('Missing raw data')

    # Synonyms
    for i, synonym_word_pair in enumerate(request.data.get('synonyms')):
        if not synonym_word_pair['word'].strip():
            errors.append('Synonyms #{} is empty'.format(i + 1))

    return errors
