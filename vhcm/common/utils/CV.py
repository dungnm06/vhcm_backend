import os
import json
from datetime import datetime
from dateutil import tz
from rest_framework.parsers import FileUploadParser
from vhcm.common.constants import *


def readimage(path):
    count = os.stat(path).st_size / 2
    with open(path, "rb") as f:
        return bytearray(f.read())


def to_abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(PROJECT_ROOT, path)


def string_to_array(input_str, separator=' '):
    return [s.strip() for s in input_str.split(separator)]


def extract_validation_messages(form, fields_map):
    messages = []
    errors = json.loads(form.errors.as_json())
    for field in errors:
        errors_in_field = [field_error['message'] for field_error in errors[field]]
        message = fields_map[field] + COLON + SPACE + (COMMA+SPACE).join(errors_in_field)
        messages.append(message)
    return messages


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'


def datetime_to_str(time, format):
    return time.strftime(format)


def normalize_django_datetime(date_str):
    # First need to chop-off un-used timezone part
    try:
        tz_idx = date_str.rindex('+')
    except ValueError:
        tz_idx = -1
    if tz_idx > 0:
        date_str = date_str[:tz_idx]

    tmp_date = datetime.strptime(date_str, DATETIME_DJANGO_DEFUALT_DDMMYYYY_HHMMSS.regex)
    normalized = tmp_date.strftime(DATETIME_DDMMYYYY_HHMMSS.regex)

    return normalized


default_utc_zone = tz.gettz('UTC')
local_zone = tz.gettz('Asia/Ho_Chi_Minh')


def utc_to_gmt7(dt):
    utc = dt.replace(tzinfo=default_utc_zone)
    local = utc.astimezone(local_zone)

    return local
