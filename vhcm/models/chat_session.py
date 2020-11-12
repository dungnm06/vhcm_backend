from django.db import models
from .user import User

# Fields
ID = 'chat_log_id'
USER_ID = 'user'
LOG = 'log'
CDATE = 'cdate'

# Chat relative
RELATIVE = [
    (1, 'User'),
    (2, 'Chatbot')
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
        choices=RELATIVE
    )
    message = models.TextField(
        verbose_name='chat message',
        null=True
    )
    intent = models.TextField(
        verbose_name='predicted intent name',
        null=True
    )
    question_types = models.TextField(
        verbose_name='predicted question types',
        null=True
    )
    action = models.SmallIntegerField(
        choices=ACTION_TYPES,
        verbose_name='chatbot reaction to user',
        null=True
    )
    recorded_time = models.DateTimeField(
        verbose_name='message send time'
    )

    class Meta:
        db_table = "chat_messages"
