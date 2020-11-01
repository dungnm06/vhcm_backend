from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'question_id'
KNOWLEDGE_DATA_ID = 'knowledge_data'
QUESTION = 'question'


class Question(models.Model):
    question_id = models.BigIntegerField(
        primary_key=True, verbose_name='question id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    question = models.TextField(
        verbose_name='question'
    )

    class Meta:
        db_table = "knowledge_data_question"
