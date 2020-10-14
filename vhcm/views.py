# Create your views here.
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer


class HelloView(APIView):
    def get(self, request):
        content = {'message': 'Hello'}
        return Response(content)


@api_view(['GET'])
def profile(request):
    user = request.user
    serialized_user = UserSerializer(user).data
    return Response({'user': serialized_user})
