from django.db import models
from .knowledge_data import KnowledgeData


# Fields
ID = 'question_id'
KNOWLEDGE_DATA_ID = 'knowledge_data'
QUESTION = 'question'
TYPE = 'type'

# Constants
WHAT = 1
WHEN = 2
WHERE = 3
WHO = 4
WHY = 5
HOW = 6
YESNO = 7
QUESTION_TYPES = [
    (WHAT, 'what'),
    (WHEN, 'when'),
    (WHERE, 'where'),
    (WHO, 'who'),
    (WHY, 'why'),
    (HOW, 'how'),
    (YESNO, 'yesno')
]
QUESTION_TYPES_T2IDX = {
    'what':     WHAT,
    'when':     WHEN,
    'where':    WHERE,
    'who':      WHO,
    'why':      WHY,
    'how':      HOW,
    'yesno':    YESNO
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
