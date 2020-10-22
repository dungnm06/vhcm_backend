from rest_framework import serializers
import vhcm.models.user as user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_model.User
        fields = [user_model.ID, user_model.USERNAME, user_model.EMAIL,
                  user_model.FULLNAME, user_model.NATIONALITY, user_model.PLACE_OF_BIRTH,
                  user_model.DATE_OF_BIRTH, user_model.ADDRESS, user_model.PHONE_NUMBER,
                  user_model.CDATE, user_model.MDATE, user_model.ACTIVE]
