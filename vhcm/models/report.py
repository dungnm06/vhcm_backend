from django.db import models
from .user import User
from .train_data import TrainData
from .knowledge_data import KnowledgeData

# Fields
ID = 'id'
REPORTER = 'reporter'
REPORTER_NOTE = 'reporter_note'
PROCESSOR = 'processor'
PROCESSOR_NOTE = 'processor_note'
REPORTED_INTENT = 'reported_intent'
FORWARD_INTENT = 'foward_intent'
QUESTION = 'question'
BOT_ANSWER = 'bot_answer'
BOT_VERSION = 'bot_version'
REPORT_DATA = 'report_data'
TYPE = 'type'
DATA = 'report_data'
STATUS = 'status'
CDATE = 'cdate'
MDATE = 'mdate'

# Report types
WRONG_ANSWER = 1
CONTRIBUTE_DATA = 2
REPORT_TYPES = [
    (WRONG_ANSWER, 'Wrong answer'),
    (CONTRIBUTE_DATA, 'Contribute data')
]
REPORT_TYPES_ARR = [
    WRONG_ANSWER,
    CONTRIBUTE_DATA
]

# Approve status
PENDING = 1
PROCESSED = 2
REJECTED = 3
APPROVE_STATUS = [
    (PENDING, 'Pending'),
    (PROCESSED, 'Processed'),
    (REJECTED, 'Rejected')
]
APPROVE_STATUS_ARR = [
    PENDING,
    PROCESSED,
    REJECTED
]


class Report(models.Model):
    id = models.AutoField(
        primary_key=True, verbose_name='report id'
    )
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reporter', verbose_name='reporter'
    )
    processor = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='processor', verbose_name='report data process user', null=True
    )
    processor_note = models.TextField(
        null=True, verbose_name='reject reason'
    )
    reported_intent = models.CharField(
        max_length=100, verbose_name='intent', db_index=True, null=True
    )
    forward_intent = models.ForeignKey(
        KnowledgeData, on_delete=models.DO_NOTHING, null=True, verbose_name='knowledge data that issue forwarded to'
    )
    question = models.TextField(
        verbose_name='user asked question', null=True
    )
    bot_answer = models.TextField(
        verbose_name='bot answered content', null=True
    )
    bot_version = models.ForeignKey(
        TrainData, on_delete=models.DO_NOTHING, verbose_name='bot version', null=True
    )
    report_data = models.TextField(
        verbose_name='report data', null=True
    )
    report_reference = models.TextField(
        verbose_name='report data reference', null=True
    )
    reporter_note = models.TextField(
        verbose_name='reporter note', null=True
    )
    type = models.SmallIntegerField(
        verbose_name='report type', choices=REPORT_TYPES
    )
    status = models.SmallIntegerField(
        verbose_name='status', choices=APPROVE_STATUS
    )
    cdate = models.DateTimeField(
        verbose_name='report recorded time', auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='report accepted/rejected date', auto_now=True
    )

    class Meta:
        db_table = "report"
