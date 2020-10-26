from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'subject_id'
KNOWLEDGE_DATA = 'knowledge_data'
TYPE = 'type'
DATA = 'subject_data'

# Subject types
SUBJECT_TYPES = ['PER', 'ORG', 'LOC', 'MISC']


class Subject(models.Model):
    subject_id = models.AutoField(
        primary_key=True, verbose_name='subject id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=5, verbose_name='subject type'
    )
    subject_data = models.TextField(
        verbose_name='subject in the knowledge datas raw sentence'
    )

    class Meta:
        db_table = "knowledge_data_subjects"
