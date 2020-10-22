import jwt
import vhcm.biz.authentication.jwt.jwt_utils as jwt_utils
from rest_framework.authentication import BaseAuthentication
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework import exceptions
from django.conf import settings
from django.contrib.auth import get_user_model
from vhcm.common.constants import ACCESS_TOKEN


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

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Access token expired')

        user = User.objects.filter(user_id=payload[jwt_utils.USER_ID]).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
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
