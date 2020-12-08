from django.db import models
from .train_data import TrainData
from .knowledge_data import KnowledgeData
from .user import User

# Fields
ID = 'id'
KNOWLEDGE_DATA_ID = 'knowledge_data_id'
TRAIN_DATA_ID = 'train_data_id'


class KnowledgeDataTrainDataLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    train_data = models.ForeignKey(TrainData, on_delete=models.CASCADE)
    edit_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        db_table = "knowledge_data_train_data_link"
        unique_together = ('knowledge_data', 'train_data', )
