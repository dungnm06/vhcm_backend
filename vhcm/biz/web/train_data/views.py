import os
from django.core import exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import COMMA, TRAIN_DATA_FOLDER, PROJECT_ROOT
from vhcm.common.utils.files import pickle_file, PICKLE_EXTENSION
from vhcm.serializers.train_data import TrainDataSerializer
from vhcm.common.dao.native_query import execute_native_query
from vhcm.biz.web.train_data.sql import GET_TRAIN_DATA
import vhcm.models.train_data as train_data_model


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()

    current_user = get_current_user(request)
    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    train_datas = train_data_model.TrainData.objects.exclude(type=3)
    serialized_data = TrainDataSerializer(train_datas, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def add(request):
    response = Response()
    result = ResponseJSON()

    current_user = get_current_user(request)
    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    errors = validate(request, 'add')
    if errors:
        result.set_status(False)
        result.set_messages(errors)
        response.data = result.to_json()
        return response

    filename = request.data.get(train_data_model.FILENAME).strip() + PICKLE_EXTENSION
    filepath = os.path.join(PROJECT_ROOT, TRAIN_DATA_FOLDER + filename)

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
def delete(request):
    pass


@api_view(['GET', 'POST'])
def all_deleted(request):
    pass


@api_view(['POST'])
def update_description(request):
    pass


def validate(request, mode):
    errors = []

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

    return errors
