from rest_framework import serializers
import vhcm.models.train_data as train_data_model
from vhcm.common.utils.CV import normalize_django_datetime


class TrainDataSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        data = super().to_representation(obj)
        # Reformat date
        data[train_data_model.CDATE] = normalize_django_datetime(data[train_data_model.CDATE])
        data[train_data_model.MDATE] = normalize_django_datetime(data[train_data_model.MDATE])
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
        data[train_data_model.CDATE] = normalize_django_datetime(data[train_data_model.CDATE])
        data[train_data_model.MDATE] = normalize_django_datetime(data[train_data_model.MDATE])
        return data

    class Meta:
        model = train_data_model.TrainData
        fields = [train_data_model.ID, train_data_model.FILENAME,
                  train_data_model.DELETE_REASON, train_data_model.DESCRIPTION,
                  train_data_model.CDATE, train_data_model.MDATE]
