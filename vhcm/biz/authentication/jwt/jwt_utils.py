import datetime
import jwt
from django.conf import settings


# Encode fields
USER_ID = 'user_id'
EXPIRE_TIME = 'exp'
ISSUE_TIME = 'iat'


def generate_access_token(user):
    from vhcm.common.config.config_manager import config_loader, LOGIN_EXPIRATION_LIMIT
    try:
        duration = config_loader.get_setting_value_int(LOGIN_EXPIRATION_LIMIT)
    except KeyError:
        duration = 30
    access_token_payload = {
        USER_ID: user,
        EXPIRE_TIME: datetime.datetime.utcnow() + datetime.timedelta(minutes=duration),
        ISSUE_TIME: datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    return access_token


# def generate_refresh_token(user, token_version):
#     refresh_token_payload = {
#         USER_ID: user.user_id,
#         EXPIRE_TIME: datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
#         ISSUE_TIME: datetime.datetime.utcnow()
#     }
#     refresh_token = jwt.encode(
#         refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256').decode('utf-8')
#
#     return refresh_token
