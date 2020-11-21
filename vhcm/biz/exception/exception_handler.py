import json
from django.http import HttpResponse
from rest_framework.decorators import renderer_classes
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from vhcm.common.response_json import ResponseJSON
from vhcm.common.utils.CH import is_error_code


def raise_exception(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    result = ResponseJSON()
    result.set_messages(['An error has occured'])

    # Now add the HTTP status code to the response. (APIException only)
    if response is not None:
        result.set_result_data({
            'status_code': response.status_code,
            'error_detail': response.data['detail']
        })
    # Other Exception types
    else:
        response = Response()
        result.set_result_data({
            'status_code': 501,
            'error_detail': str(exc)
        })

    response.data = result.to_json()
    return response


@renderer_classes([JSONRenderer])
def exception_cleaner(request, response):
    if not (hasattr(response, 'data') and response['Content-Type'] in ['application/octet-stream', 'text/plain']
            or not is_error_code(response.status_code)):
        # raise exceptions.APIException(detail='An error has occured', code=response.status_code)
        result = ResponseJSON()
        result.set_messages(['An error has occured'])
        result.set_result_data({
            'status_code': response.status_code,
            'error_detail': ''
        })
        data = result.to_json()
        new_response = HttpResponse(json.dumps(data), content_type="application/json", status=200)
        # new_response.data = result.to_json()
        setattr(new_response, 'data', data)
        response = new_response

    return response
