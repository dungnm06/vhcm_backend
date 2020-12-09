from rest_framework.decorators import api_view
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from vhcm.common.response_json import ResponseJSON
from vhcm.common.config.config_manager import config_loader, ENCRYPT_SETTING
from vhcm.biz.authentication.user_session import ensure_admin
from vhcm.common.utils.crypto import encrypt
import vhcm.models.system_settings as setting_model


@api_view(['GET', 'POST'])
def all_settings(request):
    ensure_admin(request)
    response = Response()
    result = ResponseJSON()

    settings_display = []
    for setting in setting_model.SystemSetting.objects.all():
        value = None
        hidden = False
        if setting.setting_id in ENCRYPT_SETTING:
            hidden = True
        else:
            value = setting.value

        settings_display.append({
            'setting_id': setting.setting_id,
            'setting_name': setting.setting_name,
            'description': setting.description,
            'type': setting.type,
            'value': value,
            'default': setting.default,
            'hidden': hidden,
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

    value_to_db = value
    if setting_id in ENCRYPT_SETTING:
        value_to_db = encrypt(value_to_db)
    setting.value = value_to_db
    setting.save()

    # Update in-memory setting
    config_loader.settings[setting_id][setting_model.VALUE] = value

    result.set_status(True)
    response.data = result.to_json()
    return response
