from django import forms
from django.forms import ModelForm
import vhcm.models.user as user_model
from vhcm.biz.validation.image import image_validate
from django.conf import settings


# define the class of a form
class UserEditForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        date_of_birth = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS)
        # Custom fields
        fields = [user_model.ID, user_model.FULLNAME, user_model.GENDER, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.ID_NUMBER, user_model.EMAIL]

    # Extra validations here
    def clean(self):
        # data from the form is fetched using super function
        cleaned_data = super().clean()

        # Extract the extra validation needed fields from the data
        # Avatar
        if user_model.AVATAR in cleaned_data and cleaned_data.get(user_model.AVATAR):
            f = cleaned_data.get(user_model.AVATAR).read()
            image_error = image_validate(f)
            if image_error:
                self.add_error(user_model.AVATAR, image_error)
            else:
                cleaned_data[user_model.AVATAR] = f

        return cleaned_data


# define the class of a form
class UserAddForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        # Custom fields
        fields = [user_model.USERNAME, user_model.FULLNAME, user_model.GENDER, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.ID_NUMBER, user_model.EMAIL]
