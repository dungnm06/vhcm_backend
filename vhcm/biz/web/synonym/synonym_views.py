from rest_framework.decorators import api_view
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def get_all_synonyms(request):
    response = Response()
    result = ResponseJSON()

    data = {
        'synonym_dicts': ''
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response
