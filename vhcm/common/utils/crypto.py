import base64
import hashlib
from cryptography.fernet import Fernet
from django.conf import settings

key = hashlib.md5(settings.SECRET_KEY.encode()).hexdigest()
key_64 = base64.urlsafe_b64encode(key.encode())
encryptor = Fernet(key_64)


def generate_key():
    """
    Generates a key and save it into a file
    """
    secret_key = Fernet.generate_key()
    return secret_key


def encrypt(message):
    """
    Encrypts a message
    """
    encoded_message = message.encode()
    encrypted_message = encryptor.encrypt(encoded_message).decode()

    return encrypted_message


def decrypt(encrypted_message):
    """
    Decrypts an encrypted message
    """
    encoded = encrypted_message.encode()
    decrypted_message = encryptor.decrypt(encoded).decode()

    return decrypted_message
