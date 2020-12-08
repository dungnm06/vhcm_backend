import random
import string


def get_random_password_string(length):
    """
    Random string password with letters, digits, and symbols
    """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(length))
    return password


def get_random_string(length):
    """
    Random string with the combination of lower and upper case
    """
    letters = string.ascii_letters
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return string.Template(template_file_content)
