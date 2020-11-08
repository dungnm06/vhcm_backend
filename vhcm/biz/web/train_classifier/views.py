# from rest_framework.decorators import api_view
# from rest_framework import exceptions
# from rest_framework.response import Response
# from vhcm.common.response_json import ResponseJSON
# from vhcm.biz.authentication.user_session import get_current_user
# from vhcm.biz.websocket.classifier_trainer_consumer import train_service_consumer
#
#
# @api_view(['GET', 'POST'])
# def is_process_running(request):
#     response = Response()
#     result = ResponseJSON()
#     current_user = get_current_user(request)
#
#     if not current_user.admin:
#         raise exceptions.PermissionDenied('Only superuser can use this API')
#
#     status = train_service_consumer.is_process_running()
#
#     result.set_status(True)
#     result.set_result_data(status)
#     response.data = result.to_json()
#     return response
