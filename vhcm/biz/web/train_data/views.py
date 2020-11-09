import os
from django.db import transaction
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from vhcm.biz.authentication.user_session import ensure_admin
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import COMMA, MINUS, TRAIN_DATA_FOLDER, PROJECT_ROOT
from vhcm.common.utils.files import pickle_file, PICKLE_EXTENSION
from vhcm.serializers.train_data import TrainDataSerializer, TrainDataDeletedSerializer
from vhcm.common.dao.native_query import execute_native_query
from vhcm.biz.web.train_data.sql import GET_TRAIN_DATA
import vhcm.models.train_data as train_data_model


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    train_datas = train_data_model.TrainData.objects.exclude(type=3).order_by(MINUS + train_data_model.CDATE)
    serialized_data = TrainDataSerializer(train_datas, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
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

    filename = request.data.get(train_data_model.FILENAME).strip() + PICKLE_EXTENSION
    filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)
    if os.path.exists(filepath):
        result.set_status(False)
        result.set_messages('Duplicated file name')
        response.data = result.to_json()
        return response

    include_datas = request.data.get(train_data_model.INCLUDE_DATA)
    include_datas_str = [str(id) for id in include_datas]
    sql = GET_TRAIN_DATA.format(knowledge_ids=COMMA.join(['(' + id + ')' for id in include_datas_str]))
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

    train_data = train_data_model.TrainData(
        filename=request.data.get(train_data_model.FILENAME).strip(),
        description=request.data.get(train_data_model.DESCRIPTION),
        include_data=COMMA.join(include_datas_str),
        delete_reason=None,
        type=1
    )
    train_data.save()
    serilized_data = TrainDataSerializer(train_data)

    result.set_status(True)
    result.set_result_data(serilized_data.data)
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

    filename = train_data.filename + PICKLE_EXTENSION
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
def download(request):
    ensure_admin(request)

    train_data_id = int(request.GET[train_data_model.ID])
    train_data = train_data_model.TrainData.objects.filter(id=train_data_id).first()
    if not train_data:
        return HttpResponse('Training file not exists', content_type="text/plain", status=404)

    if train_data.type == 3:
        return HttpResponse('This training data already deleted', content_type="text/plain", status=403)

    filename = train_data.filename + PICKLE_EXTENSION
    filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)
    if not os.path.exists(filepath):
        return HttpResponse('Training file not exists', content_type="text/plain", status=404)

    content = open(filepath, 'rb').read()
    response = HttpResponse(content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response


def validate(request, mode):
    errors = []

    if mode == 'update' or mode == 'delete':
        # ID
        if not (train_data_model.ID in request.data
                and isinstance(request.data.get(train_data_model.ID), int)):
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
                and isinstance(request.data.get(train_data_model.DELETE_REASON), str)):
            errors.append('Must input reason to delete train data')

    return errors
