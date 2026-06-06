import os
from cryptography.fernet import Fernet
import hashlib
import base64

def derive_salt():
    return os.urandom(16)

def derive_key(master_pw, salt):
    key = hashlib.pbkdf2_hmac(
        "sha256",
        master_pw.encode("utf-8"),
        salt,
        100000,
        dklen=32
    )

    return base64.urlsafe_b64encode(key)

def encrypt(passwd, key):
    cipher = Fernet(key)

    return cipher.encrypt(
        passwd.encode("utf-8")
    )

def decrypt(ciphertext, key):
    cipher = Fernet(key)
    plain = cipher.decrypt(ciphertext)
    
    return plain.decode("utf-8")
