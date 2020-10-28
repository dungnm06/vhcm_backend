from collections import namedtuple
from django.db import connection


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def namedtuplefetchall(cursor):
    """Return all rows from a cursor as a namedtuple"""
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def execute_native_query(sql, params, return_type='named_tuple'):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        if return_type == 'named_tuple':
            result = namedtuplefetchall(cursor)
        elif return_type == 'dict':
            result = dictfetchall(cursor)
        else:
            raise Exception('Invaild SQL query return data type')

    return result
