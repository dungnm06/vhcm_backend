from django.forms import ModelForm
from django import forms
import vhcm.models.user as user_model


# define the class of a form
class UserEditForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        # Custom fields
        fields = [user_model.ID, user_model.FULLNAME, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.EMAIL]

        # this function will be used for the validation

    # Extra validations here
    def clean(self):

        # # data from the form is fetched using super function
        # super(PostForm, self).clean()
        #
        # # extract the username and text field from the data
        # username = self.cleaned_data.get('username')
        # text = self.cleaned_data.get('text')
        #
        # # conditions to be met for the username length
        # if len(username) < 5:
        #     self._errors['username'] = self.error_class([
        #         'Minimum 5 characters required'])
        # if len(text) < 10:
        #     self._errors['text'] = self.error_class([
        #         'Post Should Contain a minimum of 10 characters'])

        # return any errors if found
        return self.cleaned_data


# define the class of a form
class UserAddForm(ModelForm):
    class Meta:
        # write the name of models for which the form is made
        model = user_model.User
        # Custom fields
        fields = [user_model.USERNAME, user_model.FULLNAME, user_model.NATIONALITY,
                  user_model.PLACE_OF_BIRTH, user_model.DATE_OF_BIRTH, user_model.ADDRESS,
                  user_model.PHONE_NUMBER, user_model.EMAIL]
