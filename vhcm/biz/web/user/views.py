import random
import string
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import exceptions
from rest_framework.response import Response
import vhcm.models.user as user_model
import vhcm.models.knowledge_data as knowledge_data_model
from vhcm.common.response_json import ResponseJSON
from vhcm.serializers.user import UserSerializer
from .forms import UserEditForm, UserAddForm
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.common.utils.CV import extract_validation_messages, ImageUploadParser
from vhcm.common.config.config_manager import CONFIG_LOADER, DEFAULT_PASSWORD
from vhcm.biz.validation.image import image_validate


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


class AddUser(APIView):
    parser_class = (ImageUploadParser,)

    def add_user(self, request):
        response = Response()
        result = ResponseJSON()
        current_user = get_current_user(request)

        if not current_user.admin:
            raise exceptions.PermissionDenied('Only superuser uses this API')

        form = UserAddForm(request.data)
        if form.is_valid():
            user = user_model.User()
            datas = form.instance
            user.username = datas.username
            user.fullname = datas.fullname
            user.gender = datas.gender
            user.set_password(CONFIG_LOADER.get_setting_value(DEFAULT_PASSWORD))
            user.nationality = datas.nationality
            user.place_of_birth = datas.place_of_birth
            user.date_of_birth = datas.date_of_birth
            user.address = datas.address
            user.email = datas.email
            user.id_number = datas.id_number
            user.phone_number = datas.phone_number

            if user_model.AVATAR in request.data and request.data.get(user_model.AVATAR):
                f = request.data.get(user_model.AVATAR).read()
                image_error = image_validate(f)
                if image_error:
                    result.set_status(False)
                    result.set_messages(image_error)
                    response.data = result.to_json()
                    return response
                user.avatar = f

            user.save()
            serialized_user = UserSerializer(user)
            result.set_result_data(serialized_user.data)
        else:
            result.set_status(False)
            result.set_messages(extract_validation_messages(form, user_model.FIELDS))
            response.data = result.to_json()
            return response

        result.set_status(True)
        response.data = result.to_json()
        return response

    def post(self, request, format=None):
        return self.add_user(request)

    def put(self, request, format=None):
        return self.add_user(request)


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

        form = UserEditForm(request.data, instance=user)
        if form.is_valid():
            datas = form.instance
            user.fullname = datas.fullname
            user.gender = datas.gender
            user.nationality = datas.nationality
            user.place_of_birth = datas.place_of_birth
            user.date_of_birth = datas.date_of_birth
            user.address = datas.address
            user.email = datas.email
            user.id_number = datas.id_number
            user.phone_number = datas.phone_number

            # BinaryField is non-editable so it cant be added to validation form
            if user_model.AVATAR in request.data and request.data.get(user_model.AVATAR):
                f = request.data.get(user_model.AVATAR).read()
                image_error = image_validate(f)
                if image_error:
                    result.set_status(False)
                    result.set_messages(image_error)
                    response.data = result.to_json()
                    return response
                user.avatar = f

            user.save()
            serialized_user = UserSerializer(user)
            result.set_result_data(serialized_user.data)
        else:
            result.set_status(False)
            result.set_messages(extract_validation_messages(form, user_model.FIELDS))
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
        knowledge_data = knowledge_data_model.KnowledgeData.objects.filter(edit_user=user)
        if knowledge_data:
            knowledge_data.update(status=0)
            knowledge_data.save()

    # Save to DB
    user.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def update_password_first_login(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)

    if current_user.first_login:
        raise exceptions.APIException('User already updated first time login password')

    if not ('password' in request.data and request.data.get('password')):
        raise exceptions.APIException('Missing password data')

    current_user.set_password(request.data.get('password'))
    current_user.first_login = True
    current_user.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def change_password(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)

    if not ('current_password' in request.data and request.data.get('current_password')):
        raise exceptions.APIException('Missing current password, couldn\'t authenticate')
    if not ('new_password' in request.data and request.data.get('new_password')):
        raise exceptions.APIException('Missing password data')
    if not current_user.check_password(request.data.get('current_password')):
        result.set_status(False)
        result.set_messages('Wrong password')
        response.data = result.to_json()
        return response

    current_user.set_password(request.data.get('new_password'))
    current_user.save()

    result.set_status(True)
    response.data = result.to_json()
    return response


# get random string password with letters, digits, and symbols
def get_random_password_string():
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(15))
    return password
