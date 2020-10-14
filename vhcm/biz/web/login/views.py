import jwt
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
from django.conf import settings
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from vhcm.biz.authentication.jwt.jwt_utils import generate_access_token, generate_refresh_token
from vhcm.serializers import UserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def login(request):
    User = get_user_model()
    username = request.data.get('username')
    password = request.data.get('password')
    response = Response()
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'Both username and password required')

    user = User.objects.filter(username=username).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('Wrong password')

    serialized_user = UserSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user, None)

    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'user': serialized_user,
    }

    return response


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def request_refresh_token(request):
    """
    To obtain a new access_token this view expects 2 important things:
        1. a cookie that contains a valid refresh_token
        2. a header 'X-CSRFTOKEN' with a valid csrf token, client app can get it from cookies "csrftoken"
    """
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    print(refresh_token)
    if refresh_token is None:
        raise exceptions.AuthenticationFailed(
            'Authentication credentials were not provided.')
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Expired refresh token')

    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('User is inactive')

    access_token = generate_access_token(user)
    return Response({'access_token': access_token})
