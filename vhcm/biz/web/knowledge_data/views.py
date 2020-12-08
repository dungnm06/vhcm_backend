from datetime import datetime
from collections import Counter
from django.db.models import Prefetch
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.db import transaction
from vhcm.common.dao.model_query import get_latest_id
from vhcm.common.response_json import ResponseJSON
import vhcm.models.user as user_model
import vhcm.models.knowledge_data as knowledge_data_model
import vhcm.models.knowledge_data_response_data as response_data_model
import vhcm.models.knowledge_data_subject as subject_model
import vhcm.models.reference_document as document_model
import vhcm.models.synonym as synonym_model
import vhcm.models.knowledge_data_reference_document_link as kd_document_model
import vhcm.models.knowledge_data_question as question_model
import vhcm.models.knowledge_data_synonym_link as kd_synonym_model
import vhcm.models.knowledge_data_generated_question as gq_model
import vhcm.models.knowledge_data_comment as comment_model
import vhcm.models.knowledge_data_review as review_model
import vhcm.models.report as report_model
import vhcm.common.config.config_manager as config
from vhcm.serializers.comment import CommentSerializer, DeletedCommentSerializer
from vhcm.biz.authentication.user_session import get_current_user, ensure_admin
from vhcm.common.constants import *
from vhcm.common.utils.CH import isInt
from .sql import GET_ALL_KNOWLEDGE_DATA, GET_ALL_TRAINABLE_KNOWLEDGE_DATA, GET_ALL_REVIEWS, GET_LATEST_KNOWLEDGE_DATA_TRAIN_DATA
from vhcm.common.dao.native_query import execute_native_query


@api_view(['GET', 'POST'])
def get_all(request):
    response = Response()
    result = ResponseJSON()

    user = get_current_user(request)
    if user.admin:
        sql_filter = ''
    else:
        sql_filter = 'WHERE kd.status != 3'
    query_data = execute_native_query(GET_ALL_KNOWLEDGE_DATA.format(user_id=user.user_id, sql_filter=sql_filter))
    result_data = {
        'knowledge_datas': [],
        'review_settings': {
            'minimum_accept': config.config_loader.get_setting_value_int(config.MINIMUM_ACCEPT),
            'maximum_reject': config.config_loader.get_setting_value_int(config.MAXIMUM_REJECT)
        }
    }
    for kd in query_data:
        kd_display = {
            'id': kd.knowledge_data_id,
            'intent': kd.intent,
            'intent_fullname': kd.intent_fullname,
            'status': kd.status,
            'create_user': kd.create_user,
            'create_user_id': kd.create_user_id,
            'edit_user': kd.edit_user,
            'edit_user_id': kd.edit_user_id,
            'cdate': kd.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'mdate': kd.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'reviews': {
                'accept': kd.accept_count,
                'reject': kd.refuse_count
            },
            'user_review': kd.user_review
        }
        result_data['knowledge_datas'].append(kd_display)

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
    knowledge_data_display = []
    knowledge_data_ids = [-1]
    for data in query_data:
        knowledge_data_ids.append(data.id)
        knowledge_data_display.append({
            'id': data.id,
            'intent': data.intent,
            'intent_fullname': data.intent_fullname,
            'edit_user': data.edit_user,
            'edit_user_id': data.edit_user_id,
            'cdate': data.cdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'mdate': data.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        })

    latest_belong_train_data_sql = GET_LATEST_KNOWLEDGE_DATA_TRAIN_DATA.format(
        knowledge_datas=COMMA.join(['(' + str(kid) + ')' for kid in knowledge_data_ids])
    )

    latest_belong_train_data_display = {}
    for kdi in knowledge_data_ids:
        latest_belong_train_data_display[kdi] = []
    del latest_belong_train_data_display[-1]

    latest_belong_train_data = execute_native_query(latest_belong_train_data_sql)
    for td in latest_belong_train_data:
        latest_belong_train_data_display[td.knowledge_data_id].append({
            'id': td.train_data_id,
            'filename': td.train_data
        })

    result_data = {
        'knowledges': knowledge_data_display,
        'train_data_info': latest_belong_train_data_display
    }

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

    user = get_current_user(request)

    knowledge_data = knowledge_data_model.KnowledgeData.objects\
        .filter(intent=intent)\
        .prefetch_related(
            'knowledgedatarefercencedocumentlink_set__reference_document',
            'knowledgedatasynonymlink_set__synonym',
            'responsedata_set',
            'subject_set',
            'question_set',
            'comment_kd__user',
            Prefetch('review_kd', queryset=review_model.Review.objects.select_related('review_user').exclude(status=review_model.DRAFT))
        )\
        .first()
    if not knowledge_data:
        raise APIException('Invalid intent id, couldnt find knowledge data')

    # Response data
    response_datas = knowledge_data.responsedata_set.all()
    response_data_display = []
    for response_data in response_datas:
        response_data_display.append({
            'type': response_data_model.RESPONSE_TYPES_IDX2T[response_data.type],
            'answer': response_data.answer
        })

    # Subject
    subjects = knowledge_data.subject_set.all()
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
    questions = knowledge_data.question_set.all()
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
    synonym_links = knowledge_data.knowledgedatasynonymlink_set.all()
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
    document_links = knowledge_data.knowledgedatarefercencedocumentlink_set.all()
    documents_display = []
    for document in document_links:
        documents_display.append({
            'id': document.reference_document.reference_document_id,
            'name': document.reference_document.reference_name,
            'page': document.page,
            'extra_info': document.extra_info
        })

    # Comments
    comments = knowledge_data.comment_kd.all()
    comments_display = []
    relative_users = {}
    for comment in comments:
        # Comment data
        display_comment = {
            comment_model.ID: comment.id,
            comment_model.USER: comment.user.user_id,
            comment_model.REPLY_TO: comment.reply_to_id,
            comment_model.COMMENT: comment.comment if (user.admin or comment.status == comment_model.VIEWABLE) else None,
            comment_model.VIEWABLE_STATUS: comment.status,
            comment_model.EDITED: comment.edited,
            comment_model.EDITABLE: comment.editable,
            comment_model.MDATE: comment.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        }
        comments_display.append(display_comment)
        # User data
        if comment.user.user_id not in relative_users:
            relative_users[comment.user.user_id] = {
                user_model.USERNAME: comment.user.username,
                user_model.FULLNAME: comment.user.fullname,
                user_model.EMAIL: comment.user.email,
                user_model.AVATAR: comment.user.avatar.url if comment.user.avatar else None
            }

    # Reviews
    reviews = knowledge_data.review_kd.all()
    accept_reviews = reviews.filter(status=review_model.ACCEPT).count()
    reject_reviews = reviews.filter(status=review_model.REJECT).count()

    # User review
    user_review = review_model.Review.objects.filter(knowledge_data=knowledge_data, review_user=user).first()
    user_review_display = None
    if user_review:
        user_review_display = {
            review_model.REVIEW_DETAIL: user_review.review_detail,
            review_model.STATUS: user_review.status,
            review_model.MDATE: user_review.mdate
        }

    result_data = {
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
        'mdate': knowledge_data.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        'comments': {
            'data': comments_display,
            'users': relative_users
        },
        'reviews': {
            'accept': accept_reviews,
            'reject': reject_reviews
        },
        'user_review': user_review_display,
        'review_settings': {
            'minimum_accept': config.config_loader.get_setting_value_int(config.MINIMUM_ACCEPT),
            'maximum_reject': config.config_loader.get_setting_value_int(config.MAXIMUM_REJECT)
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

    report_process = request.data.get('report_processing')
    report = None
    processor_note = None
    if report_process:
        try:
            report_id = int(report_process[report_model.ID])
            processor_note = report_process[report_model.PROCESSOR_NOTE]
            if not processor_note or not isinstance(processor_note, str):
                raise APIException('Report processor must leave a comment')
            report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING).first()
            if not report:
                raise APIException('Report id is invalid')
        except (KeyError, ValueError):
            raise APIException('Report process data is invalid')

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

    # Report process
    if report:
        report.status = report_model.ACCEPTED
        report.processor_note = processor_note
        report.processor = user
        report.forward_intent = knowledge_data
        report.save()
        # Note a comment of this report processing
        message = 'Report data ID:{report_id} accepted by {user} at {time}.\nProcessor note: {note}'
        message = message.format(
            report_id=report.id,
            user=user.username,
            time=datetime.now().strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            note=processor_note
        )
        comment = comment_model.Comment(
            user=user,
            knowledge_data=knowledge_data,
            comment=message,
            editable=False,
            status=comment_model.VIEWABLE
        )
        comment.save()

    # Reference document
    references = []
    next_reference_id = get_latest_id(kd_document_model.KnowledgeDataRefercenceDocumentLink, kd_document_model.ID)

    for i, reference in enumerate(request.data.get('documentReference')):
        try:
            document_id = int(reference['id'])
            document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
            if document is None:
                raise ValueError('')
            page = reference['page'] if (reference['page'] and reference['page'] > 0) else None
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
        word_type = sj['type']
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
            type=word_type,
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
            syn_words = [s.lower() for s in synonym.words.split(COMMA)]
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

    user = get_current_user(request)

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

    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=kd_id).select_related('edit_user').first()
    if knowledge_data is None:
        raise APIException('Intent id not found: ID({})'.format(kd_id))

    if knowledge_data.status == knowledge_data_model.DISABLE:
        raise APIException('Cannot edit knowledge data thats already closed')

    if user.user_id != knowledge_data.edit_user.user_id and knowledge_data.status != knowledge_data_model.AVAILABLE:
        raise APIException('You cannot edit other contributors\'s works')

    report_process = request.data.get('report_processing')
    report = None
    processor_note = None
    if report_process:
        try:
            report_id = int(report_process[report_model.ID])
            processor_note = report_process[report_model.PROCESSOR_NOTE]
            if not processor_note or not isinstance(processor_note, str):
                raise APIException('Report processor must leave a comment')
            report = report_model.Report.objects.filter(id=report_id, status=report_model.PENDING).first()
            if not report:
                raise APIException('Report id is invalid')
        except (KeyError, ValueError):
            raise APIException('Report process data is invalid')

    # Intent
    knowledge_data.intent = request.data.get('intent').strip()
    # Intent fullname
    knowledge_data.intent_fullname = request.data.get('intentFullName').strip()
    # Base response
    knowledge_data.base_response = request.data.get('baseResponse').strip()
    # Raw data
    knowledge_data.raw_data = request.data.get('rawData').strip()
    # User
    knowledge_data.edit_user = user
    # Status
    knowledge_data.status = knowledge_data_model.PROCESSING

    knowledge_data.save()

    # Report process
    if report:
        report.status = report_model.ACCEPTED
        report.processor_note = processor_note
        report.processor = user
        report.forward_intent = knowledge_data
        report.save()
        # Note a comment of this report processing
        message = 'Report data ID: {report_id} accepted by {user} at {time}.\nProcessor note: {note}'
        message = message.format(
            report_id=report.id,
            user=user.username,
            time=datetime.now().strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            note=processor_note
        )
        comment = comment_model.Comment(
            user=user,
            knowledge_data=knowledge_data,
            comment=message,
            editable=False,
            status=comment_model.VIEWABLE
        )
        comment.save()

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
            page = reference['page'] if (reference['page'] and reference['page'] > 0) else None
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
        word_type = sj['type']
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
            type=word_type,
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
            syn_words = [s.lower() for s in synonym.words.split(COMMA)]
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

    # Reset all review to draft state
    reviews = review_model.Review.objects.filter(knowledge_data=knowledge_data)
    if reviews.exists():
        reviews.update(status=review_model.DRAFT)

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def change_status(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    # Get existing Knowledge data
    kd_id = request.data.get(knowledge_data_model.ID)
    if not (kd_id and isInt(kd_id)):
        raise APIException('Invalid intent id: ID({})'.format(kd_id))

    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=kd_id).first()
    if knowledge_data is None:
        raise APIException('Intent id not found: ID({})'.format(kd_id))

    status = request.data.get(knowledge_data_model.STATUS)
    if not status:
        raise APIException('Knowledge data status must be specified')
    if status not in knowledge_data_model.CHANGEABLE_PROCESS_STATUS:
        raise APIException('Invalid knowledge data status')

    knowledge_data.status = status
    knowledge_data.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_comment(request):
    response = Response()
    result = ResponseJSON()

    errors = validate_comment(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    user = get_current_user(request)

    knowledge_data_id = request.data.get(comment_model.KNOWLEDGE_DATA) if request.method == 'POST' \
        else request.GET.get(comment_model.KNOWLEDGE_DATA)

    comments = comment_model.Comment.objects.filter(knowledge_data=knowledge_data_id).select_related('user')
    display_comments = []
    relative_users = {}
    for comment in comments:
        # Comment data
        display_comment = {
            comment_model.ID: comment.id,
            comment_model.USER: comment.user.user_id,
            comment_model.REPLY_TO: comment.reply_to_id,
            comment_model.COMMENT: comment.comment if (user.admin or comment.status == comment_model.VIEWABLE) else None,
            comment_model.VIEWABLE_STATUS: comment.status,
            comment_model.EDITED: comment.edited,
            comment_model.EDITABLE: comment.editable,
            comment_model.MDATE: comment.mdate.strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        }
        display_comments.append(display_comment)
        # User data
        if comment.user.user_id not in relative_users:
            relative_users[comment.user.user_id] = {
                user_model.USERNAME: comment.user.username,
                user_model.FULLNAME: comment.user.fullname,
                user_model.EMAIL: comment.user.email,
                user_model.AVATAR: comment.user.avatar.url if comment.user.avatar else None
            }

    result_data = {
        'data': display_comments,
        'users': relative_users
    }

    result.set_status(True)
    result.set_result_data(result_data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def post_comment(request):
    response = Response()
    result = ResponseJSON()

    errors = validate_comment(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    user = get_current_user(request)

    comment_message = request.data.get(comment_model.COMMENT)

    reply_to = request.data.get(comment_model.REPLY_TO)
    if reply_to:
        reply_to = comment_model.Comment.objects.filter(id=reply_to).first()
        if not reply_to:
            raise APIException('Invalid mentioned comment id, comment not exists')

    knowledge_data_id = request.data.get(comment_model.KNOWLEDGE_DATA)
    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=knowledge_data_id).first()
    if not knowledge_data:
        raise APIException('Invalid knowledge data id, knowledge data not exists')

    if not comment_message:
        result.set_status(False)
        result.set_messages('Comment must not empty!')
        response.data = result.to_json()
        return response

    comment = comment_model.Comment(
        user=user,
        reply_to=reply_to,
        knowledge_data=knowledge_data,
        comment=comment_message,
        status=comment_model.VIEWABLE
    )
    comment.save()

    serialized_comment_data = CommentSerializer(comment).data
    result.set_status(True)
    result.set_result_data(serialized_comment_data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def edit_comment(request):
    response = Response()
    result = ResponseJSON()

    errors = validate_comment(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    user = get_current_user(request)

    comment_id = request.data.get(comment_model.ID)
    comment = comment_model.Comment.objects.filter(id=comment_id).select_related('user').first()
    if not comment:
        raise APIException('Invalid comment id, comment not exists')
    if not comment.editable:
        raise APIException('This comment not editable')
    if user.user_id != comment.user.user_id:
        raise APIException('You cannot edit other users comment')

    comment_message = request.data.get(comment_model.COMMENT)
    if not comment_message:
        result.set_status(False)
        result.set_messages('Comment must not empty!')
        response.data = result.to_json()
        return response

    comment.comment = comment_message
    comment.edited = True
    comment.save()

    serialized_comment_data = CommentSerializer(comment).data
    result.set_status(True)
    result.set_result_data(serialized_comment_data)
    response.data = result.to_json()
    return response


@api_view(['GET'])
def delete_comment(request):
    response = Response()
    result = ResponseJSON()

    errors = validate_comment(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    user = get_current_user(request)

    comment_id = int(request.GET.get(comment_model.ID))
    comment = comment_model.Comment.objects.filter(id=comment_id).select_related('user').first()
    if not comment:
        raise APIException('Invalid comment id, comment not exists')
    if not comment.editable:
        raise APIException('Cannot delete this comment')
    if user.user_id != comment.user.user_id:
        raise APIException('You cannot delete other users comment')

    comment.status = comment_model.DELETED
    comment.save()
    if user.admin:
        serialized_comment_data = CommentSerializer(comment).data
    else:
        serialized_comment_data = DeletedCommentSerializer(comment).data
    result.set_status(True)
    result.set_result_data(serialized_comment_data)
    response.data = result.to_json()
    return response


def validate_comment(request):
    errors = []

    comment_id = request.data.get(comment_model.ID) if request.method == 'POST' \
        else request.GET.get(comment_model.ID)
    if comment_id and not isInt(comment_id):
        errors.append('Comment id is invalid')

    comment = request.data.get(comment_model.COMMENT)
    if comment and not isinstance(comment, str):
        errors.append('Comment is not filled correctly')

    knowledge_data_id = request.data.get(comment_model.KNOWLEDGE_DATA) if request.method == 'POST' \
        else request.GET.get(comment_model.KNOWLEDGE_DATA)
    if knowledge_data_id and not isInt(knowledge_data_id):
        errors.append('Knowledge data id is invalid')

    reply_to = request.data.get(comment_model.REPLY_TO)
    if reply_to and not isinstance(reply_to, int):
        errors.append('Mentioned comment id is invalid')

    return errors


@api_view(['GET', 'POST'])
def all_reviews(request):
    response = Response()
    result = ResponseJSON()

    knowledge_data_id = request.data.get(review_model.KNOWLEDGE_DATA) if request.method == 'POST' \
        else request.GET.get(review_model.KNOWLEDGE_DATA)
    if not knowledge_data_id:
        raise APIException('Missing knowledge data id.')

    reviews = execute_native_query(GET_ALL_REVIEWS.format(knowledge_data_id=knowledge_data_id))
    reviews_display = []
    for review in reviews:
        review_display = {
            'user_id': review.user_id,
            'username': review.username,
            'review': review.review,
            'status': review.status,
            'mdate': review.mdate
        }
        reviews_display.append(review_display)

    result.set_status(True)
    result.set_result_data(reviews_display)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def review_data(request):
    response = Response()
    result = ResponseJSON()

    errors = validate_review(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    user = get_current_user(request)

    knowledge_data_id = request.data.get(review_model.KNOWLEDGE_DATA)
    knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=knowledge_data_id).select_related('edit_user').first()
    if not knowledge_data:
        raise APIException('Invalid knowledge data id, knowledge data not exists')
    if knowledge_data.status != knowledge_data_model.PROCESSING:
        raise APIException('Knowledge data can only be reviewed in processing state')
    if knowledge_data.edit_user.user_id == user.user_id:
        raise APIException('You cannot review yourself works')

    all_reviews_query = review_model.Review.objects \
        .select_related('review_user') \
        .filter(knowledge_data=knowledge_data)
    review = all_reviews_query.filter(review_user=user).first()
    new = False
    if not review:
        review = review_model.Review(
            review_user=user,
            knowledge_data=knowledge_data
        )
        new = True
    review_detail = request.data.get(review_model.REVIEW_DETAIL)
    status = request.data.get(review_model.STATUS)
    if status == review_model.DRAFT:
        if review_detail:
            review.review_detail = review_detail
            review.status = review_model.DRAFT
            review.save()
        elif not new:
            review.delete()
        else:
            result.set_status(False)
            result.set_messages('Review detail must be filled')
            response.data = result.to_json()
            return response
    else:
        if not review_detail:
            result.set_status(False)
            result.set_messages('Review detail must be filled')
            response.data = result.to_json()
            return response
        else:
            review.review_detail = review_detail
            review.status = status
            review.save()
            # Knowledge data approval state update
            if all_reviews_query.filter(status=review_model.ACCEPT).count() >= config.config_loader.get_setting_value_int(config.MINIMUM_ACCEPT)\
                    and all_reviews_query.filter(status=review_model.REJECT).count() <= config.config_loader.get_setting_value_int(config.MAXIMUM_REJECT):
                knowledge_data.status = knowledge_data_model.DONE
            knowledge_data.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


def validate_review(request):
    errors = []

    detail = request.data.get(review_model.REVIEW_DETAIL)
    if detail and not isinstance(detail, str):
        errors.append('Review detail is not filled correctly')

    knowledge_data_id = request.data.get(review_model.KNOWLEDGE_DATA)
    if not (knowledge_data_id and isInt(knowledge_data_id)):
        errors.append('Knowledge data id is invalid')

    status = request.data.get(review_model.STATUS)
    if not (status and isinstance(status, int) and review_model.isValidStatus(status)):
        errors.append('Review submit type is invalid')

    return errors


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
            word_type = rd['type'].lower()
            if word_type not in response_data_model.RESPONSE_TYPES_T2IDX:
                err_rd_types.append(rd['type'])
            if not rd['answer'].strip():
                errors.append('Response data #{} is empty'.format(i + 1))
            type_check.append(word_type)
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
                errors.append('Question "{}", type not defined'.format(question.get('question', '#' + str(idx + 1))))
            elif any([t not in question_model.QUESTION_TYPES_IDX2T for t in question.get('type')]):
                errors.append(
                    'Question "{}", unknow question type included'.format(question.get('question', '#' + str(idx + 1))))

    # Raw data
    if not ('rawData' in request.data and request.data.get('rawData').strip()):
        errors.append('Missing raw data')

    # Synonyms
    for i, synonym_word_pair in enumerate(request.data.get('synonyms')):
        if not synonym_word_pair['word'].strip():
            errors.append('Synonyms #{} is empty'.format(i + 1))

    return errors
