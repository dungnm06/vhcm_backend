# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers.user import UserSerializer
from .common.response_json import ResponseJSON


class HelloView(APIView):
    def get(self, request):
        content = {'message': 'Hello'}
        return Response(content)
