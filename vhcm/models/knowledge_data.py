from django.db import models
from .user import User
from .reference_document import Refercence_Document

# Fields
ID = 'knowledge_data_id'
CREATE_USER = 'create_user_id'
EDIT_USER = 'edit_user_id'
INTENT = 'intent'
INTENT_FULLNAME = 'intent_fullname'
BASE_RESPONSE = 'base_response'
STATUS = 'status'
RAW_DATA = 'raw_data'
CDATE = 'cdate'
MDATE = 'mdate'
# Constant
ALL_STATUS = [
    0,  # Available
    1,  # Processing
    2,  # Done
    3   # Disable
]


class Knowledge_Data(models.Model):
    knowledge_data_id = models.AutoField(primary_key=True, serialize=True)
    create_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='kd_create_user_id', verbose_name='create user', db_index=True
    )
    edit_user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='kd_edit_user_id', verbose_name='edit user', db_index=True
    )
    intent = models.CharField(max_length=50, verbose_name='intent', db_index=True)
    intent_fullname = models.CharField(max_length=255, verbose_name='intent full name', db_index=True)
    base_response = models.TextField(verbose_name='base response')
    status = models.SmallIntegerField(verbose_name='status', default=0)
    raw_data = models.TextField(verbose_name='raw text data')
    cdate = models.DateTimeField(verbose_name='created date', auto_now_add=True)
    mdate = models.DateTimeField(verbose_name='modified date', auto_now=True)
    # Many-to-many relationship with Reference Document
    references = models.ManyToManyField(Refercence_Document, through='Knowledge_Data_Refercence_Document_Link')
