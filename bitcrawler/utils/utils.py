from typing import Optional
from Crypto.Cipher import AES
import hashlib
import random

def bq(text: str, caption: Optional[str] = None) -> str:
    return f"<blockquote expandable><b>{text}</b>{f' <i>{caption}</i>' if caption else ' '}</blockquote>"

def get_encrypt_name(key: int = random.randint(1, 1000)) -> str:
    text = "BitCrawler"
    key_bytes = hashlib.sha256(str(key).encode()).digest()[:16]
    cipher = AES.new(key_bytes, AES.MODE_EAX) # type: ignore
    ciphertext, _ = cipher.encrypt_and_digest(text.encode())
    return ciphertext.hex()
