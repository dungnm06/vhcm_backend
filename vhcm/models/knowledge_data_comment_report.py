from django.db import models
from .user import User
from .knowledge_data_comment import Comment
from .report import Report

# Fields
ID = 'id'
REPORT_TO = 'report_to'
REPORT = 'report'
COMMENT = 'comment'
USER_SEEN = 'user_seen'


class ReportComment(models.Model):
    id = models.AutoField(primary_key=True)
    report_to = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='user being reported to'
    )
    report = models.ForeignKey(
        Report, on_delete=models.CASCADE, verbose_name='report id'
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, verbose_name='base comment'
    )
    user_seen = models.BooleanField(
        default=False, verbose_name='is user being replied to seen the report?'
    )

    class Meta:
        db_table = "knowledge_data_comment_report"
