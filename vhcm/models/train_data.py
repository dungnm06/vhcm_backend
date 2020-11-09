from django.db import models


# Fields
ID = 'id'
FILENAME = 'filename'
DESCRIPTION = 'description'
INCLUDE_DATA = 'include_data'
DELETE_REASON = 'delete_reason'
TYPE = 'type'
CDATE = 'cdate'
MDATE = 'mdate'

# Setting types
STATUS = [
    (1, 'Available'),
    (2, 'Disable'),
    (3, 'Deleted')
]


class TrainData(models.Model):
    filename = models.CharField(
        max_length=100, verbose_name='train data file name'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    include_data = models.TextField(
        verbose_name='Excluded knowledge datas', null=True
    )
    type = models.IntegerField(
        choices=STATUS, verbose_name='Available status'
    )
    delete_reason = models.TextField(
        verbose_name='Description', null=True
    )
    cdate = models.DateTimeField(
        verbose_name='file created time', auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='details modified time', auto_now=True
    )

    class Meta:
        db_table = "train_data"
