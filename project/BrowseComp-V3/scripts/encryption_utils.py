#!/usr/bin/env python3
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def derive_key(key_str: str) -> bytes:
    """Derive 32-byte key from a passphrase using SHA-256."""
    if not isinstance(key_str, str) or not key_str:
        raise ValueError("key_str must be a non-empty string")
    return hashlib.sha256(key_str.encode("utf-8")).digest()

def encrypt_text(plaintext: str, key: bytes, iv: bytes) -> dict:
    """Encrypt plaintext with AES-256-GCM. Returns dict with iv, ciphertext, tag (base64)."""
    if plaintext is None:
        plaintext = ""
    aes = AESGCM(key)
    ct = aes.encrypt(iv, plaintext.encode("utf-8"), None)
    ciphertext, tag = ct[:-16], ct[-16:]
    return {
        "iv": base64.b64encode(iv).decode("ascii"),
        "ciphertext": base64.b64encode(ciphertext).decode("ascii"),
        "tag": base64.b64encode(tag).decode("ascii"),
    }

def decrypt_text(enc: dict, key: bytes) -> str:
    """Decrypt dict with iv/ciphertext/tag (base64)."""
    iv = base64.b64decode(enc["iv"])
    ciphertext = base64.b64decode(enc["ciphertext"])
    tag = base64.b64decode(enc["tag"])
    aes = AESGCM(key)
    plaintext = aes.decrypt(iv, ciphertext + tag, None)
    return plaintext.decode("utf-8")
