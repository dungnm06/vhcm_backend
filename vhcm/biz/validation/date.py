import datetime


def date_validate(value, format, messages=''):
    # Check valid date
    date_string = value.strip()
    try:
        parse_date = datetime.datetime.strptime(date_string, format.regex)
    except ValueError as ex:
        return messages if messages else str(ex)

    return parse_date
