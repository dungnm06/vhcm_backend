import re


def is_error_code(status_code):
    str_code = str(status_code)
    if re.fullmatch(r'[1-3][0-9]{2}', str_code):
        return False
    else:
        return True


def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
