import random
import string
import vhcm.models.user as user_model
import vhcm.models.knowledge_data_review as review_model
import vhcm.models.knowledge_data as knowledge_data_model
from django.db import transaction
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework import exceptions
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.serializers.user import UserSerializer
from .forms import AdminEditUserForm, UserAddForm, EditUserForm, AVATAR_EDIT_FLAG
from vhcm.biz.authentication.user_session import get_current_user, ensure_admin
from vhcm.common.utils.CV import extract_validation_messages, ImageUploadParser
from vhcm.common.config.config_manager import config_loader, DEFAULT_PASSWORD
from vhcm.common.dao.native_query import execute_native
from vhcm.biz.web.user.sql import DEACTIVE_USER_RELATIVES


@api_view(['GET', 'POST'])
def all_user(request):
    response = Response()
    result = ResponseJSON()

    ensure_admin(request)

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
        ensure_admin(request)
        response = Response()
        result = ResponseJSON()
        ensure_admin(request)

        form = UserAddForm(request.POST, request.FILES)
        if form.is_valid():
            user = user_model.User()
            datas = form.instance
            user.username = datas.username
            user.fullname = datas.fullname
            user.gender = datas.gender
            user.set_password(config_loader.get_setting_value(DEFAULT_PASSWORD))
            user.nationality = datas.nationality
            user.place_of_birth = datas.place_of_birth
            user.date_of_birth = datas.date_of_birth
            user.address = datas.address
            user.email = datas.email
            user.id_number = datas.id_number
            user.phone_number = datas.phone_number
            user.avatar = datas.avatar

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

    def post(self, request):
        return self.add_user(request)

    def put(self, request):
        return self.add_user(request)


class AdminEditUser(APIView):
    parser_class = (ImageUploadParser,)

    def edit_user(self, request):
        ensure_admin(request)
        response = Response()
        result = ResponseJSON()

        try:
            user_id = int(request.data.get('id'))
            user = user_model.User.objects.filter(user_id=user_id).first()
            if user is None:
                raise ValueError('')
        except ValueError:
            raise Exception('Invalid user id: {}'.format(request.data.get('id')))
        except KeyError:
            raise Exception('Missing user id')

        form = AdminEditUserForm(request.data, request.FILES, instance=user)
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
            avatar_edit_flag = form.cleaned_data.get(AVATAR_EDIT_FLAG)
            if avatar_edit_flag == '1':
                user.avatar = datas.avatar

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

    def post(self, request):
        return self.edit_user(request)

    def put(self, request):
        return self.edit_user(request)


class EditUser(APIView):
    parser_class = (ImageUploadParser,)

    def edit_user(self, request):
        response = Response()
        result = ResponseJSON()
        user = get_current_user(request)

        form = EditUserForm(request.data, request.FILES, instance=user)
        if form.is_valid():
            datas = form.instance
            user.address = datas.address
            user.email = datas.email
            user.phone_number = datas.phone_number
            avatar_edit_flag = form.cleaned_data.get(AVATAR_EDIT_FLAG)
            if avatar_edit_flag == '1':
                user.avatar = datas.avatar

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

    def post(self, request):
        return self.edit_user(request)

    def put(self, request):
        return self.edit_user(request)


@api_view(['GET', 'POST'])
@transaction.atomic
def change_status(request):
    response = Response()
    result = ResponseJSON()
    ensure_admin(request)

    user_id = int(request.data.get('id')) if request.method == 'POST' else int(request.GET.get('id'))
    if user_id:
        user = user_model.User.objects.filter(user_id=user_id, admin=False).first()
        if user:
            user.active = not user.active
            user.save()
        else:
            raise Exception('Invalid user id: {}'.format(user_id))
    else:
        raise APIException('Missing user id')

    # Change user's knowledge data status
    if not user.active:
        sql = DEACTIVE_USER_RELATIVES.format(
            review_draft_status=review_model.DRAFT,
            review_user_id=user_id,
            kd_done_status=knowledge_data_model.DONE,
            kd_available_status=knowledge_data_model.AVAILABLE,
            kd_user_id=user_id
        )
        execute_native(sql)

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
