from rest_framework.views import exception_handler
from vhcm.common.response_json import ResponseJSON


def raise_exception(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    result = ResponseJSON()
    result.set_messages(['An exception has occured'])

    # Now add the HTTP status code to the response.
    if response is not None:
        result.set_result_data({
            'status_code': response.status_code,
            'error_detail': response.data['detail']
        })

    response.data = result.to_json()
    return response
