from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.biz.nlu.language_processing import language_processor
import vhcm.models.knowledge_data as knowledge_data_model
import vhcm.models.knowledge_data_response_data as response_data_model
import vhcm.models.knowledge_data_subject as subject_model
import vhcm.models.reference_document as document_model
import vhcm.models.synonym as synonym_model
import vhcm.models.knowledge_data_reference_document_link as kd_document_model
import vhcm.models.knowledge_data_verbs as verb_model
import vhcm.models.knowledge_data_question as question_model
import vhcm.models.knowledge_data_synonym_link as kd_synonym_model
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.common.constants import *


@api_view(['GET', 'POST'])
def tokenize_sentences(request):
    response = Response()
    result = ResponseJSON()

    sentence = request.data['paragraph']
    # Named entity extract
    ner = language_processor.named_entity_reconize(sentence)
    # POS tagging
    pos_tag = language_processor.pos_tagging(sentence)
    pos_tag_tmp = []
    for pos in pos_tag:
        words = []
        for word in pos:
            words.append({
                "type": word[1],
                "value": word[0]
            })
        pos_tag_tmp.append(words)

    data = {
        'ner': ner,
        'pos': pos_tag_tmp
    }
    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


SUBMIT_TYPES = ['add', 'edit']


@api_view(['POST'])
def add(request):
    response = Response()
    result = ResponseJSON()

    errors = validate(request)
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    submit_type = request.data.get('submit_type')
    # Add new Knowledge data
    knowledge_data = knowledge_data_model.KnowledgeData()
    # Edit existing Knowledge data
    # elif submit_type == SUBMIT_TYPES[1]:
    #     data_id = int(request.data.get('id'))
    #     knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(knowledge_data_id=data_id).first()
    #     response_data = response_data_model.ResponseData.objects.filter(knowledge_data=knowledge_data)

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

    # Save the model first before create relation models
    knowledge_data.save()

    # Reference document
    references = []
    for reference in request.data.get('documentReference'):
        try:
            document_id = int(reference['id'])
            document = document_model.RefercenceDocument.objects.filter(reference_document_id=document_id).first()
            if document is None:
                raise ValueError('')
            page = int(reference['page']) if reference['page'].strip() else None
            extra_info = reference['extra_info'].strip()
            references.append(kd_document_model.KnowledgeDataRefercenceDocumentLink(
                knowledge_data=knowledge_data,
                reference_document=document,
                page=page,
                extra_info=extra_info
            ))
        except ValueError:
            errors.append('Reference document id is invalid ({})'.format(reference['id']))
    kd_document_model.KnowledgeDataRefercenceDocumentLink.objects.bulk_create(references)

    # Response data
    response_datas = []
    for rd in request.data.get('coresponse'):
        response_datas.append(response_data_model.ResponseData(
            knowledge_data=knowledge_data,
            type=response_data_model.RESPONSE_TYPES[rd['type']],
            answer=rd['answer']
        ))
    response_data_model.ResponseData.objects.bulk_create(response_datas)

    # Subjects
    verbs = []
    for sj in request.data.get('criticalData'):
        # Subject
        type = sj['type']
        subject_data = []
        for word in sj['word']:
            subject_data.append((word['type'], word['word']))
        if type == 'MISC':
            # Eg: MISC:N:Thư+V:chúc_mừng+N:năm+R:mới
            subject_data = PLUS.join([(s1[0] + COMMA + s1[1]) for s1 in subject_data])
        else:
            # Eg: LOC:làng Kim_Liên
            subject_data = SPACE.join([s1[1] for s1 in subject_data])
        subject = subject_model.Subject.objects.create(
            knowledge_data=knowledge_data,
            type=type,
            subject_data=subject_data
        )
        # Verbs
        if not sj['verb']:
            verbs.append(verb_model.Verb(
                subject=subject,
                verb_data='empty'
            ))
        else:
            verbs.append(verb_model.Verb(
                subject=subject,
                verb_data=PLUS.join([(v['type'] + COLON + v['word']) for v in sj['verb']])
            ))
    verb_model.Verb.objects.bulk_create(verbs)

    # Questions
    questions = []
    for q in request.data.get('questions'):
        questions.append(question_model.Question(
            knowledge_data=knowledge_data,
            question=q.strip()
        ))
    question_model.Question.objects.bulk_create(questions)

    # Synonyms
    kd_synonym_links = []
    for i, synonym_word_pair in enumerate(request.data.get('synonyms')):
        word = synonym_word_pair['word']
        for s_id in synonym_word_pair['synonyms']:
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
                knowledge_data=knowledge_data,
                synonym=synonym,
                word=word
            ))
    kd_synonym_model.KnowledgeDataSynonymLink.objects.bulk_create(kd_synonym_links)

    result.set_status(True)
    response.data = result.to_json()
    return response


def validate(request):
    errors = []
    # submit_type = request.data.get('submit_type')
    # if not submit_type:
    #     errors.append('Missing submit type')
    # elif submit_type not in SUBMIT_TYPES:
    #     errors.append('Submit type invalid')
    #
    # if submit_type == SUBMIT_TYPES[1]:
    #     try:
    #         data_id = int(request.data.get('id'))
    #     except (ValueError, KeyError):
    #         errors.append('Data id invalid')

    # Base response
    if not ('baseResponse' in request.data and request.data.get('baseResponse')):
        errors.append('Missing base response')

    # Response data
    if not ('coresponse' in request.data and request.data.get('coresponse')):
        errors.append('Missing response data, response data must be at least one')
    else:
        err_rd_types = []
        for i, rd in enumerate(request.data.get('coresponse')):
            if rd['type'] not in response_data_model.RESPONSE_TYPES:
                err_rd_types.append(rd['type'])
            if not rd['answer'].strip():
                errors.append('Response data #{} is empty'.format(i + 1))
        if err_rd_types:
            errors.append('Invalid response data type: {}'.format(', '.join(err_rd_types)))

    # Subjects
    if not ('criticalData' in request.data and request.data.get('criticalData')):
        errors.append('Missing subject data, must be at least one main subject')
    else:
        subjects = request.data.get('criticalData')
        for i, sj in enumerate(subjects):
            if sj['type'] not in subject_model.SUBJECT_TYPES:
                errors.append('Subject data #{} is invalid ({})'.format(i + 1, sj['type']))
            if not sj['word']:
                errors.append('Subject data #{} is empty'.format(i+1))

    # Reference document
    if not ('documentReference' in request.data and request.data.get('documentReference')):
        errors.append('Knowledge data must belong to atleast one reference document')

    # Intent
    if not ('intent' in request.data and request.data.get('intent').strip()):
        errors.append('Missing intent id')

    # Intent full name
    if not ('intentFullName' in request.data and request.data.get('intentFullName').strip()):
        errors.append('Missing intent name')

    # Questions
    if not ('questions' in request.data and request.data.get('questions')):
        errors.append('Knowledge data must has atleast 1 question')

    # Raw data
    if not ('rawData' in request.data and request.data.get('rawData').strip()):
        errors.append('Missing raw data')

    # Synonyms
    for i, synonym_word_pair in enumerate(request.data.get('synonyms')):
        if not synonym_word_pair['word'].strip():
            errors.append('Synonyms #{} is empty'.format(i + 1))

    return errors
