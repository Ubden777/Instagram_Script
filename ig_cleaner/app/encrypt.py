from cryptography.fernet import Fernet
from .config import ENCRYPTION_KEY
import base64

# This key is not safe, it should be loaded from a secure location.
# For this example, we load it from config.py which gets it from an environment variable.
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable not set.")

# The key must be a 32-byte, URL-safe base64-encoded string.
# We validate the length of the raw key before encoding.
raw_key = ENCRYPTION_KEY.encode('utf-8')
if len(raw_key) != 32:
    raise ValueError("ENCRYPTION_KEY must be exactly 32 bytes long.")

key = base64.urlsafe_b64encode(raw_key)
cipher_suite = Fernet(key)

def encrypt_data(data: str) -> str:
    """Encrypts a string and returns it as a string."""
    if not data:
        return ""
    encrypted_text = cipher_suite.encrypt(data.encode('utf-8'))
    return encrypted_text.decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts a string and returns it as a string."""
    if not encrypted_data:
        return ""
    decrypted_text = cipher_suite.decrypt(encrypted_data.encode('utf-8'))
    return decrypted_text.decode('utf-8')
