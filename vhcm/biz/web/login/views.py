import vhcm.models.user as user_model
from django.contrib.auth import get_user_model
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from vhcm.biz.authentication.jwt.jwt_utils import generate_access_token
from vhcm.serializers.user import UserSerializer
from vhcm.common.response_json import ResponseJSON
from vhcm.common.constants import ACCESS_TOKEN


@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
@ensure_csrf_cookie
def login(request):
    response = Response()
    result = ResponseJSON()
    user_query = get_user_model()
    username = request.data.get(user_model.USERNAME)
    password = request.data.get(user_model.PASSWORD)
    if (username is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'Both username and password required')

    user = user_query.objects.filter(username=username).first()
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('Wrong password')
    if not user.active:
        raise exceptions.AuthenticationFailed('User has been banned')

    serialized_user = UserSerializer(user).data
    request.session['user_id'] = user.user_id

    access_token = generate_access_token(user.user_id)
    # refresh_token = generate_refresh_token(user, None)

    response.set_cookie(key=ACCESS_TOKEN, value=access_token, httponly=True, secure=True, samesite='None')
    data = {
        'user': serialized_user,
    }
    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


# @api_view(['POST'])
# @permission_classes([AllowAny])
# @csrf_protect
# def request_refresh_token(request):
#     """
#     To obtain a new access_token this view expects 2 important things:
#         1. a cookie that contains a valid refresh_token
#         2. a header 'X-CSRFTOKEN' with a valid csrf token, client app can get it from cookies "csrftoken"
#     """
#     session = request.session
#     result = ResponseJSON()
#     user_query = get_user_model()
#     refresh_token = request.COOKIES.get('refreshtoken')
#     if refresh_token is None:
#         raise exceptions.AuthenticationFailed(
#             'Authentication credentials were not provided.')
#     try:
#         payload = jwt.decode(
#             refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
#     except jwt.ExpiredSignatureError:
#         raise exceptions.AuthenticationFailed('Expired refresh token')
#
#     user = user_query.objects.filter(user_id=payload.get(jwt_utils.USER_ID)).first()
#     if user is None:
#         raise exceptions.AuthenticationFailed('User not found')
#
#     if not user.is_active:
#         raise exceptions.AuthenticationFailed('User is inactive')
#
#     access_token = generate_access_token(user)
#     result.set_status(True)
#     result.set_result_data({'access_token': access_token})
#     return Response(result.to_json())
