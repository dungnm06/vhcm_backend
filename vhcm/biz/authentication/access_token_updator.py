import jwt
from datetime import datetime
from rest_framework import exceptions
from django.conf import settings
from vhcm.biz.authentication.jwt import jwt_utils
from vhcm.models.blacklisted_token import BlacklistedToken


class AccessTokenUpdatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        access_token = request.COOKIES.get('accesstoken')
        if not access_token \
                or (not response.data['status'] and response.data['result_data']['error_detail'] == 'Access token expired')\
                or (not response.data['status'] and response.data['result_data']['status_code'] == 403)\
                or ('auth' in request.path):
            return response

        # Decode the token
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Something wrong with access-token, do login again')

        bl_token = BlacklistedToken(token=access_token, expire=datetime.fromtimestamp(payload.get(jwt_utils.EXPIRE_TIME)))
        bl_token.save()
        # Create new access token with new expire time
        new_access_token = jwt_utils.generate_access_token(payload.get(jwt_utils.USER_ID))
        response.set_cookie(key='accesstoken', value=new_access_token, httponly=True, secure=True, samesite='None')

        return response
