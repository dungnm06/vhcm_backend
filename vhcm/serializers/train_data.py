from rest_framework import serializers
import vhcm.models.train_data as train_data_model
from datetime import datetime
from vhcm.common.constants import DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS, DATETIME_DDMMYYYY_HHMMSS


class TrainDataSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super().to_representation(obj)
        # Reformat date
        tmp_date = datetime.strptime(data[train_data_model.CDATE], DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS.regex)
        data[train_data_model.CDATE] = tmp_date.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        tmp_date = datetime.strptime(data[train_data_model.MDATE], DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS.regex)
        data[train_data_model.MDATE] = tmp_date.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        return data

    class Meta:
        model = train_data_model.TrainData
        fields = [train_data_model.ID, train_data_model.FILENAME,
                  train_data_model.TYPE, train_data_model.DESCRIPTION,
                  train_data_model.CDATE, train_data_model.MDATE]


class TrainDataDeletedSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super().to_representation(obj)
        # Reformat date
        tmp_date = datetime.strptime(data[train_data_model.CDATE], DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS.regex)
        data[train_data_model.CDATE] = tmp_date.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        tmp_date = datetime.strptime(data[train_data_model.MDATE], DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS.regex)
        data[train_data_model.MDATE] = tmp_date.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)
        return data

    class Meta:
        model = train_data_model.TrainData
        fields = [train_data_model.ID, train_data_model.FILENAME,
                  train_data_model.DELETE_REASON, train_data_model.DESCRIPTION,
                  train_data_model.CDATE, train_data_model.MDATE]
