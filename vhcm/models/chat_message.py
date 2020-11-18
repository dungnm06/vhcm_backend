from django.db import models
from .user import User
from .train_data import TrainData
from .knowledge_data_question import QUESTION_TYPES

# Fields
ID = 'chat_log_id'
USER = 'user'
SENT_FROM = 'sent_from'
MESSAGE = 'message'
INTENT = 'intent'
CDATE = 'cdate'

# Chat relative
USER_SENT = 1
BOT_SENT = 2
SENT_TYPES = [
    (USER_SENT, 'User'),
    (BOT_SENT, 'Bot')
]

INITIAL = 0
ANSWER = 1
AWAIT_CONFIRMATION = 2
CONFIRMATION_OK = 3
CONFIRMATION_NG = 4
ACTION_TYPES = [
    (INITIAL, 'initial'),
    (ANSWER, 'answer'),
    (AWAIT_CONFIRMATION, 'await'),
    (CONFIRMATION_OK, 'ok'),
    (CONFIRMATION_NG, 'ng'),
]


class Message(models.Model):
    chat_session_id = models.BigAutoField(
        primary_key=True, verbose_name='sesion id'
    )
    user = models.ForeignKey(
        User, verbose_name='chat user id', on_delete=models.CASCADE
    )
    sent_from = models.SmallIntegerField(
        choices=SENT_TYPES
    )
    message = models.TextField(
        verbose_name='chat message',
        null=True
    )
    intent = models.TextField(
        verbose_name='predicted intent name',
        null=True
    )
    question_type = models.CharField(
        verbose_name='predicted question types',
        max_length=20,
        null=True
    )
    action = models.SmallIntegerField(
        choices=ACTION_TYPES,
        verbose_name='chatbot reaction to user',
        null=True
    )
    recorded_time = models.DateTimeField(
        verbose_name='message send time',
        auto_now_add=True
    )
    data_version = models.ForeignKey(
        TrainData, verbose_name='chatbot data version', on_delete=models.CASCADE
    )

    class Meta:
        db_table = "chat_messages"
