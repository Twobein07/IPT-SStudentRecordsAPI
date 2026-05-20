import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


def get_or_create_key(key_path):
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            key = f.read()
    else:
        key = Fernet.generate_key()
        with open(key_path, 'wb') as f:
            f.write(key)
        logger.info("Generated new encryption key at %s", key_path)
    return key


def encrypt_data(plain_text, key):
    cipher = Fernet(key)
    if isinstance(plain_text, str):
        plain_text = plain_text.encode()
    return cipher.encrypt(plain_text).decode()


def decrypt_data(encrypted_text, key):
    cipher = Fernet(key)
    if isinstance(encrypted_text, str):
        encrypted_text = encrypted_text.encode()
    return cipher.decrypt(encrypted_text).decode()
