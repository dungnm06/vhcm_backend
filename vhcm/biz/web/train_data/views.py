import os
import csv
import shutil
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from vhcm.biz.authentication.user_session import ensure_admin
from vhcm.common.response_json import ResponseJSON
from vhcm.common.utils.files import pickle_file
from vhcm.serializers.train_data import TrainDataSerializer, TrainDataDeletedSerializer
from vhcm.biz.web.train_data.sql import GET_DATA, GET_TRAIN_DATA_KNOWLEDGE_DATA_INFO
from vhcm.biz.nlu.model.intent import *
from vhcm.common.utils.CH import isInt
from vhcm.common.utils.CV import utc_to_gmt7
from vhcm.common.constants import DATETIME_DDMMYYYY_HHMMSS
from vhcm.common.dao.native_query import execute_native_query
import vhcm.models.train_data as train_data_model
import vhcm.models.knowledge_data as knowledge_data_model
from vhcm.models.knowledge_data_train_data_link import KnowledgeDataTrainDataLink
from vhcm.common.utils.files import zipdir, ZIP_EXTENSION


@api_view(['GET', 'POST'])
def all_train_data(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    train_datas = train_data_model.TrainData.objects.exclude(type=3).order_by(MINUS + train_data_model.CDATE)
    serialized_data = TrainDataSerializer(train_datas, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_trainable(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    train_datas = train_data_model.TrainData.objects.filter(type=1).order_by(MINUS + train_data_model.CDATE)
    serialized_data = TrainDataSerializer(train_datas, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
@transaction.atomic
def add(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    errors = validate(request, 'add')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    filename = request.data.get(train_data_model.FILENAME).strip()
    try:
        train_data_check = train_data_model.TrainData.objects.filter(filename=filename).first()
        if train_data_check:
            result.set_status(False)
            result.set_messages('Duplicated file name')
            response.data = result.to_json()
            return response
        storepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)
        if not os.path.exists(storepath):
            os.makedirs(storepath)
        filepath = os.path.join(storepath, TRAIN_DATA_FILE_NAME)
        include_datas = request.data.get(train_data_model.INCLUDE_DATA)
        if not (include_datas and isinstance(include_datas, list)):
            raise APIException('Create train data form is malformed')

        sql = GET_DATA.format(knowledge_ids=COMMA.join(['(' + str(kd_id) + ')' for kd_id in include_datas]))
        query_data = execute_native_query(sql)
        questions = []
        intent = []
        types = []

        for data in query_data:
            questions.append(data.generated_question)
            intent.append(data.intent)
            types.append(data.type)

        train_data_to_pickle = {
            'question': questions,
            'intent': intent,
            'type': types
        }

        pickle_file(train_data_to_pickle, filepath)

        # Save intent data
        knowledge_datas = knowledge_data_model.KnowledgeData.objects\
            .filter(knowledge_data_id__in=include_datas)\
            .prefetch_related(
                'knowledgedatarefercencedocumentlink_set__reference_document',
                'knowledgedatasynonymlink_set__synonym',
                'responsedata_set', 'subject_set'
            ).select_related('edit_user')
        intent_data_filepath = os.path.join(storepath, INTENT_DATA_FILE_NAME)
        intent_references_for_file_saving = {}
        reference_document_for_file_saving = {}
        synonyms_for_file_saving = {}
        with open(intent_data_filepath, 'w', newline='', encoding=UTF8) as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            # Titles
            writer.writerow(INTENT_DATA_COLUMNS)
            # Intents
            for kd in knowledge_datas:
                # ID
                intent_id = kd.knowledge_data_id
                # Name
                intent_name = kd.intent
                # Fullname
                intent_fullname = kd.intent_fullname
                # Raw data
                intent_rawdata = kd.raw_data
                # Base response
                intent_base_response = kd.base_response
                # Response answers
                responses_query = kd.responsedata_set.all()
                intent_responses = HASH.join((str(response.type) + UNDERSCORE + response.answer) for response in responses_query)
                # Subjects + Verbs
                subjects_query = kd.subject_set.all()
                subjects = []
                verbs = []
                for subject in subjects_query:
                    subjects.append(str(subject.type) + COLON + subject.subject_data)
                    verbs.append(subject.verbs if subject.verbs else 'empty')
                intent_subjects = HASH.join(subjects)
                intent_verbs = HASH.join(verbs)
                # References
                references = kd.knowledgedatarefercencedocumentlink_set.all()
                for reference in references:
                    reference_document = reference.reference_document
                    if intent_id not in intent_references_for_file_saving:
                        intent_references_for_file_saving[intent_id] = {}
                    if reference_document.reference_document_id not in reference_document_for_file_saving:
                        reference_document_for_file_saving[reference_document.reference_document_id] = {
                            'name': reference_document.reference_name,
                            'link': reference_document.link,
                            'author': reference_document.author
                        }
                    intent_references_for_file_saving[intent_id][reference_document.reference_document_id] = {
                        'page': reference.page,
                        'extra_info': reference.extra_info
                    }
                references_data = {
                    'intent_references': intent_references_for_file_saving,
                    'documents': reference_document_for_file_saving
                }
                # Synonyms
                synonyms = kd.knowledgedatasynonymlink_set.all()
                intent_synonyms = []
                for synonym_link in synonyms:
                    synonym_id = synonym_link.synonym.synonym_id
                    if synonym_id not in synonyms_for_file_saving:
                        synonyms_for_file_saving[synonym_id] = {
                            synonym_model.MEANING: synonym_link.synonym.meaning,
                            synonym_model.WORDS: synonym_link.synonym.words.split(COMMA),
                            synonym_model.NAMED_ENTITY: synonym_link.synonym.ne_synonym
                        }
                    intent_synonyms.append(synonym_id)
                intent_synonyms = COMMA.join(str(i) for i in intent_synonyms)

                # Write to csv
                writer.writerow([intent_id, intent_name, intent_fullname, intent_rawdata, intent_base_response,
                                 intent_responses, intent_subjects, intent_verbs, intent_synonyms])

        # Write references data to file
        references_filepath = os.path.join(storepath, REFERENCES_FILE_NAME)
        with open(references_filepath, 'w', encoding=UTF8) as fp:
            json.dump(references_data, fp, indent=4)

        # Write synonyms data to file
        synonyms_filepath = os.path.join(storepath, SYNONYMS_FILE_NAME)
        with open(synonyms_filepath, 'w', encoding=UTF8) as fp:
            json.dump(synonyms_for_file_saving, fp, indent=4)

        zipdir(storepath + ZIP_EXTENSION, storepath)

        train_data = train_data_model.TrainData(
            filename=filename,
            description=request.data.get(train_data_model.DESCRIPTION),
            type=1
        )
        train_data.save()

        # Create m2m relation
        kd_td_links = []
        for kd in knowledge_datas:
            kd_td_links.append(KnowledgeDataTrainDataLink(knowledge_data=kd, train_data=train_data, edit_user=kd.edit_user))
        KnowledgeDataTrainDataLink.objects.bulk_create(kd_td_links)

        serilized_data = TrainDataSerializer(train_data)
        result.set_status(True)
        result.set_result_data(serilized_data.data)
        response.data = result.to_json()
        return response
    except Exception as e:
        print('Failed to create training data')
        print(e)
        raise APIException('Failed to create training data')
    finally:
        # Clear temp files
        storepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)
        if os.path.exists(storepath):
            shutil.rmtree(storepath)


@api_view(['GET', 'POST'])
def get(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    errors = validate(request, 'get')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    train_data_id = request.data.get(train_data_model.ID) if request.method == 'POST' else request.GET.get(train_data_model.ID)
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        raise APIException('Training file id not exists')

    knowledge_data_info = execute_native_query(GET_TRAIN_DATA_KNOWLEDGE_DATA_INFO.format(id=train_data_id))
    knowledge_datas_display = []
    for kd in knowledge_data_info:
        knowledge_datas_display.append({
            'id': kd.knowledge_data_id,
            'intent': kd.intent,
            'intent_fullname': kd.intent_fullname,
            'edit_user': kd.edit_user
        })

    train_data_display = {
        'filename': train_data.filename,
        'description': train_data.description,
        'type': train_data.type,
        'delete_reason': train_data.delete_reason,
        'cdate': utc_to_gmt7(train_data.cdate).strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        'mdate': utc_to_gmt7(train_data.mdate).strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
        'knowledge_datas': knowledge_datas_display
    }

    result.set_status(True)
    result.set_result_data(train_data_display)
    response.data = result.to_json()
    return response


@api_view(['POST'])
@transaction.atomic
def delete(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    errors = validate(request, 'delete')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    delete_reason = request.data.get(train_data_model.DELETE_REASON).strip()

    train_data_id = int(request.data[train_data_model.ID])
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        raise APIException('Training file id not exists')

    if train_data.type == 3:
        raise APIException('This training data already deleted')

    train_data.delete_reason = delete_reason
    train_data.type = 3
    train_data.save()

    filename = train_data.filename + ZIP_EXTENSION
    filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)

    if os.path.exists(filepath):
        os.remove(filepath)

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def all_deleted(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    train_datas = train_data_model.TrainData.objects.filter(type=3).order_by(MINUS + train_data_model.MDATE)
    serialized_data = TrainDataDeletedSerializer(train_datas, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def update_description(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    errors = validate(request, 'update')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    train_data_id = int(request.data[train_data_model.ID])
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        raise APIException('Training file id not exists')
    if train_data.type == 3:
        raise APIException('This training data already deleted')

    train_data.description = request.data.get(train_data_model.DESCRIPTION).strip()
    train_data.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['GET'])
def on_off_data(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    errors = validate(request, 'onoff')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    train_data_id = int(request.GET.get(train_data_model.ID))
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        raise APIException('Training file id not exists')
    if train_data.type == 3:
        raise APIException('This training data already deleted')

    train_data.type = 1 if train_data.type == 2 else 2
    train_data.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['GET'])
def download(request):
    ensure_admin(request)

    train_data_id = int(request.GET[train_data_model.ID])
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        return HttpResponse('Training file not exists', content_type="text/plain", status=404)

    if train_data.type == 3:
        return HttpResponse('This training data already deleted', content_type="text/plain", status=403)

    filename = train_data.filename + ZIP_EXTENSION
    path = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)
    if not os.path.exists(path):
        return HttpResponse('Training file not exists', content_type="text/plain", status=404)

    content = open(path, 'rb').read()
    response = HttpResponse(content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


def validate(request, mode):
    errors = []

    if mode == 'update' or mode == 'delete' or mode == 'onoff' or mode == 'get':
        # ID
        train_data_id = request.data.get(train_data_model.ID) if request.method == 'POST' else request.GET.get(
            train_data_model.ID)
        if not (train_data_id and isInt(train_data_id)):
            errors.append('Invalid training file id')

    if mode == 'update' or mode == 'add':
        # Description
        if not (train_data_model.DESCRIPTION in request.data
                and isinstance(request.data.get(train_data_model.DESCRIPTION), str)
                and request.data.get(train_data_model.DESCRIPTION).strip()):
            errors.append('Description cannot be blank')

    if mode == 'add':
        # Filename
        if not (train_data_model.FILENAME in request.data
                and isinstance(request.data.get(train_data_model.FILENAME), str)
                and request.data.get(train_data_model.FILENAME).strip()):
            errors.append('Filename cannot be blank')
        # Exclude knowledge datas
        if not (train_data_model.INCLUDE_DATA in request.data and isinstance(request.data.get(train_data_model.INCLUDE_DATA), list)):
            errors.append('Form data is malformed')
        elif len(request.data.get(train_data_model.INCLUDE_DATA)) < 1:
            errors.append('Training data must include at least 1 knowledge data')

    if mode == 'delete':
        # Delete reason
        if not (train_data_model.DELETE_REASON in request.data
                and isinstance(request.data.get(train_data_model.DELETE_REASON), str)
                and request.data.get(train_data_model.DELETE_REASON).strip()):
            errors.append('Must input reason to delete train data')

    return errors
