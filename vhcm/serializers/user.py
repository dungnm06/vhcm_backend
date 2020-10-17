from rest_framework import serializers
from vhcm.models.user import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email',
                  'fullname', 'nationality', 'place_of_birth',
                  'date_of_birth', 'address', 'phone_number',
                  'cdate', 'mdate', 'active', 'admin']
