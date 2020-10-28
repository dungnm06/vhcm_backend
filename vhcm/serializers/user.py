from rest_framework import serializers
from datetime import datetime
import vhcm.models.user as user_model
from vhcm.common.constants import DATETIME_DJANGO_DEFUALT, DATETIME_DDMMYYYY


class UserSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super().to_representation(obj)
        # Reformat date
        tmp_date = datetime.strptime(data[user_model.DATE_OF_BIRTH], DATETIME_DJANGO_DEFUALT.regex)
        data[user_model.DATE_OF_BIRTH] = tmp_date.strftime(DATETIME_DDMMYYYY.regex)
        return data

    class Meta:
        model = user_model.User
        fields = [user_model.ID, user_model.USERNAME, user_model.AVATAR, user_model.EMAIL,
                  user_model.FULLNAME, user_model.NATIONALITY, user_model.PLACE_OF_BIRTH,
                  user_model.DATE_OF_BIRTH, user_model.ADDRESS, user_model.PHONE_NUMBER,
                  user_model.CDATE, user_model.MDATE, user_model.ACTIVE, user_model.ADMIN,
                  user_model.FIRST_LOGIN]
