import os
import json
from rest_framework.parsers import FileUploadParser
from vhcm.common.constants import COMMA, COLON, SPACE, PROJECT_ROOT


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
