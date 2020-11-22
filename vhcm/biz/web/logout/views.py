import jwt
# from datetime import datetime
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.conf import settings
from vhcm.common.response_json import ResponseJSON
# from vhcm.models import BlacklistedToken
from vhcm.biz.authentication.jwt import jwt_utils
from vhcm.biz.authentication.user_session import sessions_data
from vhcm.common.constants import ACCESS_TOKEN


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def logout(request):
    response = Response()
    result = ResponseJSON()
    access_token = request.COOKIES.get(ACCESS_TOKEN)

    if not access_token:
        raise exceptions.AuthenticationFailed('You are not even logged in')
    else:
        # Clear access-token from header cookie
        response.set_cookie(key=ACCESS_TOKEN, value='', httponly=True, secure=True, samesite='None', max_age=0)
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload[jwt_utils.USER_ID]
            sessions_data[user_id] = None
        except jwt.ExpiredSignatureError:
            # if access-token already expired so dont need to do anything else
            pass

        # if payload:
        #     # Add current access-token to blacklist
        #     bl_token = BlacklistedToken(token=access_token,
        #                                 expire=datetime.fromtimestamp(payload.get(jwt_utils.EXPIRE_TIME)))
        #     bl_token.save()

    request.session['user_id'] = None

    result.set_status(True)
    response.data = result.to_json()
    return response
