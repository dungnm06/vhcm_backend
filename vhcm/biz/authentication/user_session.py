import jwt
import vhcm.biz.authentication.jwt.jwt_utils as jwt_utils
import vhcm.models.user as user_model
from django.conf import settings
from rest_framework import exceptions
from vhcm.common.constants import ACCESS_TOKEN

sessions_data = {}


def get_current_user(request):
    user_id = -1
    # Trying to read from session
    if request.session.get('user_id'):
        user_id = request.session.get('user_id')
    # In case of user restart browser makes session not existed
    # Try to read user id from access token
    elif request.COOKIES.get(ACCESS_TOKEN):
        access_token = request.COOKIES.get(ACCESS_TOKEN)
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = int(payload.get(jwt_utils.USER_ID))
            request.session['user_id'] = user_id
        except (jwt.ExpiredSignatureError, ValueError):
            raise exceptions.AuthenticationFailed('Access token expired')

    user = sessions_data.get(user_id)
    if not user:
        user = user_model.User.objects.filter(user_id=user_id).first()
        if user:
            sessions_data[user_id] = user

    return user


def ensure_admin(request):
    current_user = get_current_user(request)
    if not current_user:
        raise exceptions.AuthenticationFailed('Authentication credentials not provided')
    if current_user and not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')
