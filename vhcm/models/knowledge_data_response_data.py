from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'response_data_id'
KNOWLEDGE_DATA_ID = 'knowledge_data'
TYPE = 'type'
ANSWER = 'answer'
# Constants
RESPONSE_TYPES = {
    1: 'what',
    2: 'when',
    3: 'where',
    4: 'who',
    5: 'why',
    6: 'how',
    7: 'yesno'
}


class ResponseData(models.Model):
    response_data_id = models.AutoField(
        primary_key=True, verbose_name='response data id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    type = models.SmallIntegerField(
        verbose_name='type of question'
    )
    answer = models.TextField(
        verbose_name='answer string'
    )

    class Meta:
        db_table = "knowledge_data_response_data"
