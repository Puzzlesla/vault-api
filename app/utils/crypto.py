from cryptography.fernet import Fernet, InvalidToken
from app.core.config import get_settings

def get_cipher():
    settings = get_settings()
    return Fernet(settings.AES_MASTER_KEY)

def encrypt_data(plain_text: str) -> str:
    cipher = get_cipher()
    encrypted_data = cipher.encrypt(plain_text.encode())
    return encrypted_data.decode()

def decrypt_data(encrypted_text: str) -> str:
    cipher = get_cipher()
    try:
        decrypted_data = cipher.decrypt(encrypted_text.encode())
    except InvalidToken:
        raise ValueError("Invalid encrypted data")
    return decrypted_data.decode()