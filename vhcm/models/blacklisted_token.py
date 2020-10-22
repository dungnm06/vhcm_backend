from django.db import models

# Fields
TOKEN = 'token'
EXPIRE_TIME = 'expire'


class BlacklistedToken(models.Model):
    token = models.TextField(
        primary_key=True, verbose_name='blacklisted access token'
    )
    expire = models.DateTimeField(
        db_index=True, verbose_name='expire time'
    )

    class Meta:
        db_table = "blacklisted_token"
