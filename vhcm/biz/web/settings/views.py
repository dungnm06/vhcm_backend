from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.config.config_manager import config_loader
from vhcm.biz.authentication.user_session import ensure_admin
import vhcm.models.system_settings as setting_model


@api_view(['GET', 'POST'])
def all_settings(request):
    ensure_admin(request)
    response = Response()
    result = ResponseJSON()

    settings_display = []
    for setting in config_loader.settings:
        settings_display.append({
            'setting_id': setting.setting_id,
            'setting_name': setting.setting_name,
            'description': setting.description,
            'type': setting.type,
            'value': setting.value,
            'default': setting.default,
            'mdate': setting.mdate
        })

    result.set_status(True)
    result.set_result_data(settings_display)
    response.data = result.to_json()
    return response


@api_view(['POST'])
def edit(request):
    ensure_admin(request)
    response = Response()
    result = ResponseJSON()

    setting_id = request.data.get(setting_model.ID)
    if not setting_id:
        raise APIException('Setting id is invalid')

    setting = config_loader.get_setting(setting_id)
    if not setting:
        raise APIException('Setting id is invalid, setting not found')

    value = request.data.get(setting_model.VALUE)
    setting.value = value
    setting.save()

    result.set_status(True)
    response.data = result.to_json()
    return response
