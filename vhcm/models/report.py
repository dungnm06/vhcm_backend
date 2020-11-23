from django.db import models
from .user import User

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
LACK_DATA = 2
REPORT_TYPES = [
    (WRONG_ANSWER, 'Wrong answer'),
    (LACK_DATA, 'Lack of data')
]
REPORT_TYPES_ARR = [
    WRONG_ANSWER,
    LACK_DATA
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
    report_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='report_user', verbose_name='reported user'
    )
    process_user = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name='process_user', verbose_name='report data process user', null=True
    )
    reject_reason = models.TextField(
        null=True, verbose_name='reject reason'
    )
    report_data = models.TextField(
        verbose_name='report data', null=True
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
