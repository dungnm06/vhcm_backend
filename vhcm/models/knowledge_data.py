from django.db import models
from .user import User
from .reference_document import RefercenceDocument
from .synonym import Synonym
from .train_data import TrainData

# Fields
ID = 'knowledge_data_id'
CREATE_USER = 'create_user'
EDIT_USER = 'edit_user'
INTENT = 'intent'
INTENT_FULLNAME = 'intent_fullname'
BASE_RESPONSE = 'base_response'
STATUS = 'status'
RAW_DATA = 'raw_data'
CDATE = 'cdate'
MDATE = 'mdate'
# Constant
AVAILABLE = 0
PROCESSING = 1
DONE = 2
DISABLE = 3
PROCESS_STATUS = [
    (AVAILABLE, 'Available'),
    (PROCESSING, 'Processing'),
    (DONE, 'Done'),
    (DISABLE, 'Disable')
]
PROCESS_STATUS_DICT = {
    AVAILABLE: 'Available',
    PROCESSING: 'Processing',
    DONE: 'Done',
    DISABLE: 'Disable'
}


class KnowledgeData(models.Model):
    knowledge_data_id = models.AutoField(primary_key=True, serialize=True)
    create_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='kd_create_user_id', verbose_name='create user', db_index=True
    )
    edit_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='kd_edit_user_id', verbose_name='edit user', db_index=True
    )
    intent = models.CharField(max_length=100, verbose_name='intent', db_index=True, unique=True)
    intent_fullname = models.CharField(max_length=255, verbose_name='intent full name', db_index=True)
    base_response = models.TextField(verbose_name='base response')
    status = models.SmallIntegerField(verbose_name='status', choices=PROCESS_STATUS, default=1, db_index=True)
    raw_data = models.TextField(verbose_name='raw text data')
    cdate = models.DateTimeField(verbose_name='created date', auto_now_add=True)
    mdate = models.DateTimeField(verbose_name='modified date', auto_now=True, db_index=True)
    # Many-to-many relationship with other models
    references = models.ManyToManyField(RefercenceDocument, through='KnowledgeDataRefercenceDocumentLink')
    synonym = models.ManyToManyField(Synonym, through='KnowledgeDataSynonymLink')
    train_data = models.ManyToManyField(TrainData, through='KnowledgeDataTrainDataLink')

    class Meta:
        db_table = "knowledge_data"
