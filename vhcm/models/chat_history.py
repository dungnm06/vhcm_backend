from django.db import models
from .user import User

# Fields
ID = 'chat_log_id'
USER_ID = 'user'
LOG = 'log'
CDATE = 'cdate'


class ChatHistory(models.Model):
    chat_history_id = models.AutoField(
        primary_key=True, verbose_name='log id', serialize=True
    )
    user = models.ForeignKey(
        User, verbose_name='chat user id', on_delete=models.CASCADE
    )
    log = models.TextField(
        verbose_name='chat history', blank=True
    )
    cdate = models.DateTimeField(
        verbose_name='chat recorded time', auto_now_add=True
    )

    class Meta:
        db_table = "chat_history"
