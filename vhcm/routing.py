from django.urls import re_path
from vhcm.biz.websocket.intent_classifier_consumer import IntentClassifierConsumer

websocket_urlpatterns = [
    re_path(r'wss/intent-classifier/$', IntentClassifierConsumer.as_asgi()),
]
