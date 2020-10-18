from django.db import models
from .knowledge_data import KnowledgeData
from .reference_document import RefercenceDocument


# Fields
KNOWLEDGE_DATA_ID = 'knowledge_data'
REFERENCE_DOCUMENT_ID = 'reference_document'
PAGE = 'page'
EXTRA_INFO = 'extra_info'


class KnowledgeDataRefercenceDocumentLink(models.Model):
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    reference_document = models.ForeignKey(RefercenceDocument, on_delete=models.CASCADE)
    page = models.SmallIntegerField(
        verbose_name='document page number'
    )
    extra_info = models.TextField(
        verbose_name='extra info on reference document'
    )

    class Meta:
        db_table = "knowledge_data_reference_document_link"
