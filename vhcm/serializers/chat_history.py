from rest_framework import serializers
import vhcm.models.chat_history as chat_history_model


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = chat_history_model.ChatHistory
        fields = [chat_history_model.ID, chat_history_model.USER,
                  chat_history_model.SESSION_START, chat_history_model.SESSION_END]
