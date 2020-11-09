from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'question_id'
KNOWLEDGE_DATA_ID = 'knowledge_data'
QUESTION = 'question'
TYPE = 'type'

# Constants
QUESTION_TYPES = [
    (1, 'what'),
    (2, 'when'),
    (3, 'where'),
    (4, 'who'),
    (5, 'why'),
    (6, 'how'),
    (7, 'yesno')
]
QUESTION_TYPES_T2IDX = {
    'what':     1,
    'when':     2,
    'where':    3,
    'who':      4,
    'why':      5,
    'how':      6,
    'yesno':    7
}
QUESTION_TYPES_IDX2T = {v: k for k, v in QUESTION_TYPES_T2IDX.items()}


class Question(models.Model):
    question_id = models.BigIntegerField(
        primary_key=True, verbose_name='question id', serialize=True
    )
    knowledge_data = models.ForeignKey(KnowledgeData, on_delete=models.CASCADE)
    question = models.TextField(
        verbose_name='question'
    )
    type = models.CharField(
        max_length=13,
        verbose_name='question type'
    )

    class Meta:
        db_table = "knowledge_data_question"
