from django.db import models
from .user import User
from .knowledge_data import KnowledgeData

# Fields
ID = 'id'
USER = 'review_user'
KNOWLEDGE_DATA = 'knowledge_data'
STATUS = 'status'
REVIEW_DETAIL = 'review_detail'
CDATE = 'cdate'
MDATE = 'mdate'

# Constants
ACCEPT = 1
REJECT = 2
DRAFT = 3

REVIEW_TYPES = [
    (ACCEPT, 'accept'),
    (REJECT, 'reject'),
    (DRAFT, 'draft')
]
REVIEW_TYPES_2 = [ACCEPT, REJECT, DRAFT]


class Review(models.Model):
    id = models.BigAutoField(primary_key=True)
    review_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='review_user', verbose_name='review user'
    )
    knowledge_data = models.ForeignKey(
        KnowledgeData, on_delete=models.CASCADE, related_name='review_kd'
    )
    status = models.SmallIntegerField(
        choices=REVIEW_TYPES, verbose_name='review action types', db_index=True
    )
    review_detail = models.TextField(
        verbose_name='review detail'
    )
    cdate = models.DateTimeField(
        verbose_name='created date', auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='modified date', auto_now=True
    )

    class Meta:
        db_table = "knowledge_data_review"


def isValidStatus(status):
    return status in REVIEW_TYPES_2
