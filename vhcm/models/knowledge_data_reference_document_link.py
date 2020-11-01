from django.db import models
from .knowledge_data import KnowledgeData
from .reference_document import RefercenceDocument


# Fields
ID = 'id'
KNOWLEDGE_DATA_ID = 'knowledge_data'
REFERENCE_DOCUMENT_ID = 'reference_document'
PAGE = 'page'
EXTRA_INFO = 'extra_info'


class KnowledgeDataRefercenceDocumentLink(models.Model):
    id = models.BigIntegerField(primary_key=True)
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    reference_document = models.ForeignKey(RefercenceDocument, on_delete=models.CASCADE)
    page = models.SmallIntegerField(
        null=True, blank=True, default=None,
        verbose_name='document page number'
    )
    extra_info = models.TextField(
        null=True,
        verbose_name='extra info on reference document'
    )

    class Meta:
        db_table = "knowledge_data_reference_document_link"
