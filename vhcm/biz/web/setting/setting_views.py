from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view
from rest_framework import exceptions
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
import vhcm.models.system_settings as setting_model
from vhcm.biz.authentication.user_session import get_current_user
from vhcm.serializers.setting import SettingSerializer


@api_view(['GET', 'POST'])
def all(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)
    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    settings = setting_model.SystemSetting.objects.all()
    serialized_settings = SettingSerializer(settings, many=True)

    result.set_status(True)
    result.set_result_data(serialized_settings.data)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def update(request):
    response = Response()
    result = ResponseJSON()
    current_user = get_current_user(request)
    if not current_user.admin:
        raise exceptions.PermissionDenied('Only superuser can use this API')

    try:
        settings = request.data.get('settings')
        updates = []
        for setting in settings:
            model = setting_model.SystemSetting.objects.filter(setting_id=setting[setting_model.ID]).first()
            if model is None:
                raise APIException('Setting ' + setting[setting_model.ID] + ' is not found')
            model.value = setting[setting_model.VALUE]
            updates.append(model)
        setting_model.SystemSetting.objects.bulk_update(updates, [setting_model.VALUE])
    except KeyError:
        raise APIException('Form data is malformed')

    result.set_status(True)
    result.set_result_data({})
    response.data = result.to_json()
    return response
