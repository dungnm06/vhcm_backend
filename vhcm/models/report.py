from django.db import models
from .chat_history import ChatHistory

# Fields
ID = 'report_id'
CHAT_HISTORY_ID = 'chat_id'
DATA = 'report_data'
TYPE = 'type'
STATUS = 'status'
CDATE = 'cdate'


class Report(models.Model):
    report_id = models.AutoField(
        primary_key=True, verbose_name='report id', serialize=True
    )
    chat_id = models.ForeignKey(
        ChatHistory, verbose_name='chat history id', on_delete=models.CASCADE
    )
    report_data = models.TextField(
        verbose_name='report data', null=True
    )
    type = models.SmallIntegerField(
        verbose_name='report type'
    )
    status = models.SmallIntegerField(
        verbose_name='status'
    )
    cdate = models.DateTimeField(
        verbose_name='report recorded time', auto_now_add=True
    )

    class Meta:
        db_table = "report"
