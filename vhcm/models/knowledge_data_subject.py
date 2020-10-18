from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'subject_id'
KNOWLEDGE_DATA = 'knowledge_data'
DATA = 'subject_data'


class Subject(models.Model):
    subject_id = models.AutoField(
        primary_key=True, verbose_name='subject id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    subject_data = models.TextField(
        verbose_name='subject in the knowledge datas raw sentence'
    )

    class Meta:
        db_table = "knowledge_data_subjects"
