from django.db import models
from .knowledge_data_question import Question


# Fields
ID = 'generated_question_id'
QUESTION_ID = 'question'
DATA = 'generated_question'
STATUS = 'accept_status'

ACCEPT_STATUS = {
    1: True,
    0: False
}


class GeneratedQuestion(models.Model):
    generated_question_id = models.BigIntegerField(
        primary_key=True, verbose_name='generated question id', serialize=True
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    generated_question = models.TextField(
        verbose_name='generated question'
    )
    accept_status = models.BooleanField(
        verbose_name='accepted status'
    )

    class Meta:
        db_table = "knowledge_data_generated_question"
