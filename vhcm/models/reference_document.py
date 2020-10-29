from django.db import models
from .user import User

# Fields
ID = 'reference_document_id'
CREATE_USER = 'create_user'
LAST_EDIT_USER = 'last_edit_user'
NAME = 'reference_name'
LINK = 'link'
COVER = 'cover'
AUTHOR = 'author'
CDATE = 'cdate'
MDATE = 'mdate'

# Fields key:name map
FIELDS = {
    ID: 'User ID',
    CREATE_USER: 'Reference Document Created User',
    LAST_EDIT_USER: 'Reference Document Last Edited User',
    NAME: 'Reference Document Name',
    LINK: 'Resource Link',
    COVER: 'Cover',
    AUTHOR: 'Author',
    CDATE: 'CDATE',
    MDATE: 'MDATE',
}


class RefercenceDocument(models.Model):
    reference_document_id = models.AutoField(
        primary_key=True, serialize=True, verbose_name='reference document id'
    )
    create_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rd_create_user_id', verbose_name='create user', db_index=True
    )
    last_edit_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rd_last_edit_user_id', verbose_name='last edit user', db_index=True
    )
    reference_name = models.CharField(
        max_length=100, blank=False, default='', verbose_name='reference name', db_index=True
    )
    link = models.TextField(null=True, blank=True, verbose_name='reference urls')
    cover = models.BinaryField(null=True, blank=True, verbose_name='document cover')
    author = models.TextField(blank=False, default='', verbose_name='document author', db_index=True)
    cdate = models.DateTimeField(verbose_name='created date', auto_now_add=True)
    mdate = models.DateTimeField(verbose_name='modified date', auto_now=True)

    class Meta:
        db_table = "reference_document"
