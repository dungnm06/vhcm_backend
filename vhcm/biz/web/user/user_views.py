import datetime
import random
import string
import io
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import exceptions
from rest_framework.response import Response
import vhcm.models.user as user_model
import vhcm.models.knowledge_data as knowledge_data_model
import vhcm.common.config.config_manager as config
from vhcm.common.response_json import ResponseJSON
from vhcm.serializers.user import UserSerializer
from .user_form import UserForm
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.common.utils.CV import extract_validation_messages, ImageUploadParser
from vhcm.common.constants import COMMA
from PIL import Image


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)
    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    all_users = user_model.User.objects.filter()
    serialized_user = UserSerializer(all_users, many=True)

    data = {
        'users': serialized_user.data
    }

    result.set_status(True)
    result.set_result_data(data)
    response.data = result.to_json()
    return response


@api_view(['GET', 'POST'])
def get(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)

    try:
        user_id = int(request.data.get('id')) if request.method == 'POST' else int(request.GET.get('id'))
        user = user_model.User.objects.filter(user_id=user_id).first()
        if user is None:
            raise ValueError('')
    except (ValueError, TypeError):
        raise Exception('Invalid user id: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing user id')

    if not current_user.admin and user.admin:
        raise exceptions.PermissionDenied('Only superuser can view this user infomations')

    if current_user.user_id != user.user_id and not current_user.admin:
        raise exceptions.PermissionDenied('You dont have right to view this user infomations')

    serialized_user = UserSerializer(user).data

    result.set_status(True)
    result.set_result_data(serialized_user)
    response.data = result.to_json()
    return response


class EditUser(APIView):
    parser_class = (ImageUploadParser,)

    def edit_user(self, request):
        response = Response()
        result = ResponseJSON()
        current_user = get_current_user(request)

        try:
            user_id = int(request.data.get('id'))
            user = user_model.User.objects.filter(user_id=user_id).first()
            if user is None:
                raise ValueError('')
        except ValueError:
            raise Exception('Invalid user id: {}'.format(request.data.get('id')))
        except KeyError:
            raise Exception('Missing user id')

        if not current_user.admin and user.admin:
            raise exceptions.PermissionDenied('Only superuser can edit this user infomations')

        if current_user.user_id != user.user_id and not current_user.admin:
            raise exceptions.PermissionDenied('You dont have right to edit this user infomations')

        form = UserForm(request.data)
        if form.is_valid():
            datas = form.instance
            user.fullname = datas.fullname
            user.nationality = datas.nationality
            user.place_of_birth = datas.place_of_birth
            user.date_of_birth = datas.date_of_birth
            user.address = datas.address
            user.email = datas.email
            user.phone_number = datas.phone_number

            if user_model.AVATAR in request.data and request.data[user_model.AVATAR]:
                f = request.data[user_model.AVATAR].read()
                image = Image.open(io.BytesIO(f))
                if image.format not in config.CONFIG_LOADER.get_setting_value_array(config.ACCEPT_IMAGE_FORMAT, COMMA):
                    result.set_status(False)
                    result.set_messages('Only accept jpg, png image file format')
                    response.data = result.to_json()
                    return response
                user.avatar = f

            user.save()
        else:
            result.set_status(False)
            result.set_messages(extract_validation_messages(form))
            response.data = result.to_json()
            return response

        result.set_status(True)
        response.data = result.to_json()
        return response

    def post(self, request, format=None):
        return self.edit_user(request)

    def put(self, request, format=None):
        return self.edit_user(request)


@api_view(['GET', 'POST'])
def change_status(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)

    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    try:
        user_id = int(request.data.get('id')) if request.method == 'POST' else int(request.GET.get('id'))
        user = user_model.User.objects.filter(user_id=user_id, admin=False).first()
        if user is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid user id: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing user id')

    user.active = not user.active

    # Change user's knowledge data status
    if not user.active:
        knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(edit_user=user).update(status=0)
        knowledge_data.save()

    # Save to DB
    user.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


# get random string password with letters, digits, and symbols
def get_random_password_string():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(15))
    return password


def validate(request):
    errors = []
    # Fullname
    if not ('fullname' in request.data and request.data.get('fullname').strip()):
        errors.append('Missing user\'s fullname')

    # Nationality
    if not ('nationality' in request.data and request.data.get('nationality').strip()):
        errors.append('Missing user\'s nationality')

    # Place of birth
    if not ('place_of_birth' in request.data and request.data.get('place_of_birth').strip()):
        errors.append('Missing user\'s place of birth')

    # Date of birth
    if not ('date_of_birth' in request.data and request.data.get('date_of_birth').strip()):
        errors.append('Missing user\'s date of birth')
    else:
        # Check valid date
        date_string = request.data.get('date_of_birth').strip()
        format = "%Y-%m-d"
        try:
            datetime.datetime.strptime(date_string, format)
        except ValueError:
            print("Invalid date string format. Only accept YYYY-MM-DD")

    # Address
    if not ('address' in request.data and request.data.get('address').strip()):
        errors.append('Missing user\'s address')

    return errors
