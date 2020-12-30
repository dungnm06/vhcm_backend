from django.db import models
from .user import User
from .train_data import TrainData

# Fields
ID = 'id'
USER = 'user'
SENT_FROM = 'sent_from'
MESSAGE = 'message'
INTENT = 'intent'
QUESTION_TYPE = 'question_type'
ACTION = 'action'
RECORDED_TIME = 'recorded_time'
DATA_VERSION = 'data_version'

# Chat relative
USER_SENT = 1
BOT_SENT = 2
SYSTEM_SENT = 3
SENT_TYPES = [
    (USER_SENT, 'User'),
    (BOT_SENT, 'Bot'),
    (SYSTEM_SENT, 'System')
]

INITIAL = 0
ANSWER = 1
AWAIT_CONFIRMATION = 2
CONFIRMATION_OK = 3
CONFIRMATION_NG = 4
ERROR_COMMAND = 5
ERROR_SERVER = 6
ACTION_TYPES = [
    (INITIAL, 'initial'),
    (ANSWER, 'answer'),
    (AWAIT_CONFIRMATION, 'await'),
    (CONFIRMATION_OK, 'ok'),
    (CONFIRMATION_NG, 'ng'),
    (ERROR_COMMAND, 'error_command'),
    (ERROR_SERVER, 'error_server'),
]


class ChatState(models.Model):
    id = models.BigAutoField(
        primary_key=True, verbose_name='sesion id'
    )
    user = models.ForeignKey(
        User, verbose_name='chat user id', on_delete=models.CASCADE
    )
    sent_from = models.SmallIntegerField(
        choices=SENT_TYPES
    )
    user_question = models.TextField(
        verbose_name='user asked question', null=True
    )
    # Recorded message (From both user side and system side)
    message = models.TextField(
        verbose_name='chat message',
        null=True
    )
    recorded_time = models.DateTimeField(
        verbose_name='message send time',
        auto_now_add=True
    )
    data_version = models.ForeignKey(
        TrainData, verbose_name='chatbot data version', on_delete=models.CASCADE
    )
    # Bot state
    predicted_intent = models.TextField(
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
    reportable_bot_states = models.TextField(
        verbose_name='indexes of reportable bot states', null=True
    )
    hcm_question = models.BooleanField(
        verbose_name='is user asking hcm related question', null=True
    )
    context_question = models.BooleanField(
        verbose_name='is user asking context question', null=True
    )
    # System state
    system_state_idx = models.SmallIntegerField(
        verbose_name='index of current system process state', null=True
    )
    system_processing_type = models.SmallIntegerField(
        verbose_name='system processing type', null=True
    )
    system_processing_report_type = models.SmallIntegerField(
        verbose_name='system processing report type', null=True
    )
    system_input_data_type = models.TextField(
        verbose_name='current user input data type', null=True
    )
    system_tmp_report_data = models.TextField(
        verbose_name='temp user report data', null=True
    )
    system_tmp_report_note = models.TextField(
        verbose_name='temp user report note', null=True
    )
    system_tmp_report_bot_state = models.SmallIntegerField(
        verbose_name='temp bot state being reported', null=True
    )

    class Meta:
        db_table = "chat_state"
