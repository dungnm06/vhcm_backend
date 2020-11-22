import jwt
import vhcm.biz.authentication.jwt.jwt_utils as jwt_utils
from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
# import vhcm.models.blacklisted_token as bl_token_model
from vhcm.common.constants import ACCESS_TOKEN
from vhcm.biz.authentication.user_session import sessions_data


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        # Return the failure reason instead of an HttpResponse
        return reason


class JWTAuthentication(BaseAuthentication):
    """
        custom authentication class for DRF and JWT
        https://github.com/encode/django-rest-framework/blob/master/rest_framework/authentication.py
    """

    def authenticate(self, request):
        User = get_user_model()
        access_token = request.COOKIES.get(ACCESS_TOKEN)

        # Authentication credentials not provided
        if not access_token:
            return None

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload[jwt_utils.USER_ID]

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Access token expired')

        # blacklisted = bl_token_model.BlacklistedToken.objects.filter(token=access_token).first()
        # if blacklisted is not None:
        #     raise exceptions.AuthenticationFailed('Access token expired')

        user = sessions_data.get(user_id)
        if not user:
            user = User.objects.filter(user_id=user_id).first()
            sessions_data[user_id] = user

        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.active:
            raise exceptions.AuthenticationFailed('User is inactive')

        self.enforce_csrf(request)
        return user, None

    @staticmethod
    def enforce_csrf(request):
        """
        Enforce CSRF validation
        """
        check = CSRFCheck()
        # populates request.META['CSRF_COOKIE'], which is used in process_view()
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            # CSRF failed, bail with explicit error message
            raise exceptions.PermissionDenied('CSRF Failed: %s' % reason)
