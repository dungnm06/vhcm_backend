from django.db import models
from .user import User
from .train_data import TrainData

# Fields
ID = 'id'
REPORT_USER = 'report_user'
PROCESS_USER = 'process_user'
DATA = 'report_data'
TYPE = 'type'
STATUS = 'status'
CDATE = 'cdate'

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
ACCEPTED = 2
REJECTED = 3
APPROVE_STATUS = [
    (PENDING, 'Pending'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected')
]
APPROVE_STATUS_ARR = [
    PENDING,
    ACCEPTED,
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
    reject_reason = models.TextField(
        null=True, verbose_name='reject reason'
    )
    intent = models.CharField(
        max_length=100, verbose_name='intent', db_index=True, null=True
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

    class Meta:
        db_table = "report"
