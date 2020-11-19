from django.db import models
from .user import User
from .knowledge_data import KnowledgeData

# Constants
VIEWABLE = 1
DELETED = 2
VIEW_TYPES = [
    (VIEWABLE, 'viewable'),
    (DELETED, 'deleted')
]


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment_user', verbose_name='comment user'
    )
    mentioned_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True,
        related_name='comment_mentioned_comment', verbose_name='mentioned comment'
    )
    knowledge_data = models.ForeignKey(
        KnowledgeData, on_delete=models.CASCADE,
        related_name='comment_kd', verbose_name='knowledge data the comment belong to'
    )
    comment = models.TextField(
        verbose_name='comment text'
    )
    status = models.SmallIntegerField(
        choices=VIEW_TYPES, verbose_name='comment viewable status'
    )
    cdate = models.DateTimeField(
        verbose_name='created date', auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='modified date', auto_now=True
    )

    class Meta:
        db_table = "knowledge_data_comment"
