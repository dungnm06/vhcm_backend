from django.db import models


# Fields
ID = 'setting_id'
NAME = 'setting_name'
DESCRIPTION = 'description'
VALUE = 'value'
DEFAULT = 'default'
CDATE = 'cdate'
MDATE = 'mdate'

# Setting types
SETTING_TYPES = [
    (1, 'System'),
    (2, 'NLP'),
    (3, 'Review process')
]


class SystemSetting(models.Model):
    setting_id = models.CharField(
        primary_key=True, max_length=50, verbose_name='report id'
    )
    setting_name = models.CharField(
        max_length=100, verbose_name='setting name'
    )
    description = models.TextField(
        verbose_name='setting description', null=True, blank=True
    )
    type = models.IntegerField(
        choices=SETTING_TYPES, verbose_name='setting type'
    )
    value = models.TextField(
        verbose_name='value', null=True, blank=True
    )
    default = models.TextField(
        verbose_name='default value'
    )
    cdate = models.DateTimeField(
        verbose_name='setting created time', auto_now_add=True
    )
    mdate = models.DateTimeField(
        verbose_name='setting modified time', auto_now=True
    )

    class Meta:
        db_table = "system_settings"
