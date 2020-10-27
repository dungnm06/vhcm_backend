import vhcm.models.user as user_model
from vhcm.common.response_json import ResponseJSON
from rest_framework.response import Response
from vhcm.serializers.user import UserSerializer
from rest_framework.decorators import api_view
from vhcm.biz.authentication.user_session import get_current_user
from rest_framework import exceptions


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()
    all_users = user_model.User.objects.filter(is_superuser=False)
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
        user_id = int(request.data.get('id'))
        user = user_model.User.objects.filter(user_id=user_id)
        if user is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid user id: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing user id')

    if not current_user.is_admin() and user.is_admin():
        raise exceptions.PermissionDenied('Only superuser can view this user infomations')

    serialized_user = UserSerializer(user).data

    result.set_status(True)
    result.set_result_data(serialized_user)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def edit(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)

    try:
        user_id = int(request.data.get('id'))
        user = user_model.User.objects.filter(user_id=user_id)
        if user is None:
            raise ValueError('')
    except ValueError:
        raise Exception('Invalid user id: {}'.format(request.data.get('id')))
    except KeyError:
        raise Exception('Missing user id')

    if not current_user.is_admin() and user.is_admin():
        raise exceptions.PermissionDenied('Only superuser can view this user infomations')

    result.set_status(True)
    result.set_result_data({})
    response.data = result.to_json()
    return response


def validate(request):
    errors = []
    # Fullname
    if not ('fullname' in request.data and request.data.get('fullname').strip()):
        errors.append('Missing user\'s fullname')

    # Nationality
    if not ('nationality' in request.data and request.data.get('nationality').strip()):
        errors.append('Missing user\'s nationality')

    # Place of birth
    if not ('place_of_birth' in request.data and request.data.get('place_of_birth')):
        errors.append('Missing user\'s place of birth')

    # Date of birth
    if not ('date_of_birth' in request.data and request.data.get('date_of_birth').strip()):
        errors.append('Missing user\'s date of birth')
    else:
        # Check valid date
        date_string = '12-25-2018'
        format = "%Y-%m-d"
        try:
            # datetime.datetime.strptime(date_string, format)
            print("This is the correct date string format.")
        except ValueError:
            print("This is the incorrect date string format. It should be YYYY-MM-DD")

    return errors
