from rest_framework import serializers
import vhcm.models.system_settings as setting_model


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = setting_model.SystemSetting
        fields = [setting_model.ID, setting_model.NAME, setting_model.DESCRIPTION, setting_model.VALUE,
                  setting_model.DEFAULT, setting_model.CDATE, setting_model.MDATE]
