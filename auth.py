import bcrypt
from getpass import getpass
from crypto import derive_key, derive_salt

def create_master_passwd():
    while True:
        pw1 = getpass("Enter master password: ")
        pw2 = getpass("Confirm password: ")

        if pw1 == pw2:
            return pw1

        print("Passwords do not match. Try again.")
        return None

def set_new_mp():
    while True:
        pw1 = getpass("Enter new master password: ")
        pw2 = getpass("Confirm password: ")

        if pw1 == pw2:
            return pw1

        print("Passwords do not match. Try again.")
        return None

def hash_pw(passwd):
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

def verify_pw(passwd, stored_hash):
    pw_bytes = passwd.encode('utf-8')
    hashed = hash_pw(pw_bytes)
    return bcrypt.checkpw(hashed, stored_hash)

MAX_ATTEMPTS = 5

def login(stored_hash, stored_salt):
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        pw = getpass("Enter master password: ")
        if verify_pw(pw, stored_hash):
            key = derive_key(pw, stored_salt)
            return key

        attempts += 1

        print(
            f"Incorrect password. "
            f"{MAX_ATTEMPTS - attempts} attempts remaining."
        )

    return None

    




