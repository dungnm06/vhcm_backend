from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'subject_id'
KNOWLEDGE_DATA = 'knowledge_data'
TYPE = 'type'
DATA = 'subject_data'
VERBS = 'verbs'

# Subject types
SUBJECT_TYPES = ['PER', 'ORG', 'LOC', 'MISC']


class Subject(models.Model):
    subject_id = models.BigIntegerField(
        primary_key=True, verbose_name='subject id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=5, verbose_name='subject type'
    )
    subject_data = models.TextField(
        verbose_name='subject in the knowledge datas raw sentence'
    )
    verbs = models.TextField(
        verbose_name='verbs belong to the subject', null=True
    )

    class Meta:
        db_table = "knowledge_data_subjects"
