from rest_framework import serializers
import vhcm.models.train_data as train_data_model


class TrainDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = train_data_model.TrainData
        fields = [train_data_model.ID, train_data_model.FILENAME,
                  train_data_model.TYPE, train_data_model.DESCRIPTION,
                  train_data_model.CDATE, train_data_model.MDATE]


class TrainDataDeletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = train_data_model.TrainData
        fields = [train_data_model.ID, train_data_model.FILENAME,
                  train_data_model.DELETE_REASON, train_data_model.DESCRIPTION,
                  train_data_model.CDATE, train_data_model.MDATE]
