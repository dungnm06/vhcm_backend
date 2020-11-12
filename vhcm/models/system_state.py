from django.db import models


# Fields
NAME = 'name'
STATE = 'state'


class SystemStates(models.Model):
    name = models.CharField(
        primary_key=True, max_length=50, verbose_name='report id'
    )
    state = models.TextField(
       verbose_name='setting name', null=True
    )

    class Meta:
        db_table = "system_states"
