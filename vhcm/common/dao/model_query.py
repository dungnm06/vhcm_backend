from django.core.exceptions import ObjectDoesNotExist
from django.db import connection


def get_latest_id(model, id_field):
    try:
        latest = model.objects.latest(id_field)
        field_value = getattr(latest, id_field)
        next_id = field_value + 1
    except ObjectDoesNotExist:
        next_id = 1
    return next_id


def is_table_exists(table_name):
    return table_name in connection.introspection.table_names()
