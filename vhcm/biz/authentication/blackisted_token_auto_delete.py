from timeloop import Timeloop
from datetime import timedelta, datetime
from vhcm.models.blacklisted_token import BlacklistedToken


def run_auto_delete_expire_token_task():
    tl = Timeloop()

    @tl.job(interval=timedelta(seconds=600))
    def delete_expired_token():
        now = datetime.now()
        expired_token = BlacklistedToken.objects.filter(expire__lte=now)
        delete_num = len(expired_token)
        expired_token.delete()
        print(delete_num, 'expired access-token deleted')

    tl.start(block=False)
