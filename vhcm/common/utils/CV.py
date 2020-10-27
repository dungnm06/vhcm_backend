import os
import json
from pathlib import Path


def readimage(path):
    count = os.stat(path).st_size / 2
    with open(path, "rb") as f:
        return bytearray(f.read())


def to_abs_path(path):
    if os.path.isabs(path):
        return path
    else:
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        return os.path.join(project_root, path)


def string_to_array(input_str, separator=' '):
    return [s.strip() for s in input_str.split(separator)]


def extract_validation_messages(form):
    messages = []
    errors = json.loads(form.errors.as_json())
    for field in errors:
        messages.extend([field_error['message'] for field_error in errors[field]])

    return messages
