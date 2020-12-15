import pickle
from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import DATETIME_DDMMYYYY_HHMMSS
from vhcm.common.dao.native_query import execute_native_query
from vhcm.biz.web.chat_history.sql import GET_ALL_CHATLOG
from vhcm.common.utils.CV import utc_to_gmt7
import vhcm.models.chat_history as chat_history_model


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()

    all_logs = execute_native_query(GET_ALL_CHATLOG)
    display_results = []
    for log in all_logs:
        display_results.append({
            'log_id': log.log_id,
            'user_id': log.user_id,
            'username': log.username,
            'session_start': utc_to_gmt7(log.session_start).strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'session_end': utc_to_gmt7(log.session_end).strftime(DATETIME_DDMMYYYY_HHMMSS.regex),
            'bot_version': log.bot_version
        })

    result.set_status(True)
    result.set_result_data(display_results)
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
