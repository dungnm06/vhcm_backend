from django.db import models
from .knowledge_data import Knowledge_Data
from .reference_document import Refercence_Document


class Knowledge_Data_Refercence_Document_Link(models.Model):
    knowledge_data = models.ForeignKey(Knowledge_Data, on_delete=models.CASCADE)
    reference_document = models.ForeignKey(Refercence_Document, on_delete=models.CASCADE)
    page = models.SmallIntegerField(verbose_name='document page number')
    extra_info = models.TextField(verbose_name='extra info on reference document')
