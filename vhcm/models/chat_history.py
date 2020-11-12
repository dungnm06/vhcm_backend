from datetime import datetime

from django.db import models
from .user import User

# Fields
ID = 'log_id'
USER = 'user'
LOG = 'log'
SESSION_START = 'session_start'
SESSION_END = 'session_end'


class ChatHistory(models.Model):
    log_id = models.AutoField(
        primary_key=True, verbose_name='log id', serialize=True
    )
    user = models.ForeignKey(
        User, verbose_name='chat user id', on_delete=models.CASCADE
    )
    log = models.BinaryField(
        verbose_name='chat history', blank=True
    )
    session_start = models.DateTimeField(
        verbose_name='chat session start time', default=datetime.now
    )
    session_end = models.DateTimeField(
        verbose_name='chat session end time', auto_now_add=True
    )

    class Meta:
        db_table = 'chat_history'
