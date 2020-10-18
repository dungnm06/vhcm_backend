from django.db import models
from .knowledge_data_subject import Subject


# Fields
ID = 'verb_id'
SUBJECT_ID = 'subject'
DATA = 'verb_data'


class Verb(models.Model):
    verb_id = models.AutoField(
        primary_key=True, verbose_name='verb id', serialize=True
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    verb_data = models.TextField(
        verbose_name='verb belong to subject in the knowledge datas raw sentence'
    )

    class Meta:
        db_table = "knowledge_data_verbs"
