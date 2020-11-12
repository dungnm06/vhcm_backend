from django.urls import re_path
from vhcm.biz.websocket.classifier_trainer_consumer import ClassifierConsumer
from vhcm.biz.websocket.chatbot_consumer import ChatbotConsumer

websocket_urlpatterns = [
    re_path(r'ws/train-classifier/$', ClassifierConsumer.as_asgi()),
    re_path(r'ws/chat/$', ChatbotConsumer.as_asgi()),
]
