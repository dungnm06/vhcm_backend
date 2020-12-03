import jwt
from django.conf import settings
from vhcm.biz.authentication.jwt import jwt_utils
# from vhcm.models.blacklisted_token import BlacklistedToken
from vhcm.common.constants import ACCESS_TOKEN


def access_token_updator(request, response):
    access_token = request.COOKIES.get('accesstoken')
    if not access_token:
        return response
    # Decode the token
    try:
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return response

    # Push old token to blacklist, prevent suspicious uses
    # (currently not using this due to frontend cannot handle api call synchronously)
    # bl_token = BlacklistedToken(token=access_token, expire=datetime.fromtimestamp(payload.get(jwt_utils.EXPIRE_TIME)))
    # bl_token.save()

    # Create new access token with new expire time
    new_access_token = jwt_utils.generate_access_token(payload.get(jwt_utils.USER_ID))
    response.set_cookie(key=ACCESS_TOKEN, value=new_access_token, httponly=True, secure=True, samesite='None')

    return response
