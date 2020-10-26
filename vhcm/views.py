# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON


class HelloView(APIView):
    def get(self, request):
        content = {'message': 'Hello'}
        return Response(content)

    def post(self, request):
        response = Response()
        result = ResponseJSON()
        debug_data = request.data
        content = {'message': 'Hello'}
        result.set_status(True)
        result.set_result_data(content)
        response.data = result.to_json()
        return response
