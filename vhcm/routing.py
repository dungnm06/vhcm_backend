from django.urls import re_path
from vhcm.biz.websocket.classifier_trainer_consumer import ClassifierConsumer

websocket_urlpatterns = [
    re_path(r'ws/train-classifier/$', ClassifierConsumer.as_asgi()),
]
