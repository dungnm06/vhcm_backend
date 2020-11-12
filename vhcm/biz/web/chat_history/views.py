import pickle
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import MINUS
from vhcm.common.utils.files import pickle_file, unpickle_file
from vhcm.serializers.chat_history import ChatHistorySerializer
import vhcm.models.chat_history as chat_history_model


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()

    all_logs = chat_history_model.ChatHistory.objects.all().order_by(MINUS + chat_history_model.SESSION_END)
    serialized_data = ChatHistorySerializer(all_logs, many=True)

    result.set_status(True)
    result.set_result_data(serialized_data.data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get(request):
    response = Response()
    result = ResponseJSON()

    try:
        log_id = request.data[chat_history_model.ID] if request.method == 'POST' else request.GET[
            chat_history_model.ID]
        log_id = int(log_id)
    except (KeyError, ValueError):
        raise APIException('Invalid log id')

    log = chat_history_model.ChatHistory.objects.filter(log_id=log_id).first()
    if not log:
        raise APIException('Invalid log id, chat log not exists')

    log_details = pickle.loads(log.log)

    result.set_status(True)
    result.set_result_data(log_details)
    response.data = result.to_json()
    return response
