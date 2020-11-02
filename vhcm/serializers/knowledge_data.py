from rest_framework import serializers
import vhcm.models.knowledge_data as knowledge_data_model


class KnowledgeDataSerializer(serializers.ModelSerializer):
    create_user_username = serializers.CharField(source='create_user.username')
    edit_user_username = serializers.CharField(source='edit_user.username')

    class Meta:
        model = knowledge_data_model.KnowledgeData
        fields = [knowledge_data_model.INTENT, knowledge_data_model.INTENT_FULLNAME,
                  knowledge_data_model.PROCESS_STATUS, knowledge_data_model.CREATE_USER + '_username',
                  knowledge_data_model.EDIT_USER + '_username', knowledge_data_model.CDATE, knowledge_data_model.MDATE]
