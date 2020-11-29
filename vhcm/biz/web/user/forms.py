from django import forms
from django.forms import ModelForm
import vhcm.models.user as user_model
from django.conf import settings


AVATAR_EDIT_FLAG = 'avatar_edit'


# define the class of a form
class AdminEditUserForm(ModelForm):
    avatar_edit = forms.IntegerField(max_value=1, min_value=0, required=True)

    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        date_of_birth = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
        # Custom fields
        fields = [user_model.ID, user_model.FULLNAME, user_model.GENDER, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.ID_NUMBER, user_model.EMAIL, AVATAR_EDIT_FLAG, user_model.AVATAR]


class EditUserForm(ModelForm):
    avatar_edit = forms.IntegerField(max_value=1, min_value=0, required=True)

    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        date_of_birth = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
        # Custom fields
        fields = [user_model.ADDRESS, user_model.PHONE_NUMBER, user_model.EMAIL, AVATAR_EDIT_FLAG, user_model.AVATAR]


# define the class of a form
class UserAddForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        # Custom fields
        fields = [user_model.USERNAME, user_model.FULLNAME, user_model.GENDER, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.ID_NUMBER, user_model.EMAIL, user_model.AVATAR]
