from django.db import models
from .synonym import Synonym
from .knowledge_data import KnowledgeData

# Fields
ID = 'id'
KNOWLEDGE_DATA_ID = 'knowledge_data_id'
SYNONYM = 'synonym'
WORD = 'words'


class KnowledgeDataSynonymLink(models.Model):
    id = models.BigIntegerField(primary_key=True)
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    synonym = models.ForeignKey(Synonym, on_delete=models.CASCADE)
    word = models.TextField(
        verbose_name='word thats synonym dict linking with'
    )

    class Meta:
        db_table = "knowledge_data_synonym_link"
        unique_together = ('knowledge_data', 'synonym', 'word',)
