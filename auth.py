import bcrypt
from getpass import getpass

def create_master_passwd():
    while True:
        pw1 = getpass("Enter master password: ")
        pw2 = getpass("Confirm password: ")

        if pw1 == pw2:
            return pw1

        print("Passwords do not match. Try again.")

def hash_pw(passwd):
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

def verify_pw(passwd, stored_hash):
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.checkpw(pw_bytes, stored_hash)

MAX_ATTEMPTS = 5

def login(stored_hash):
    attempts = 0

    while attempts < MAX_ATTEMPTS:
        pw = input("Enter master password: ")

        if verify_pw(pw, stored_hash):
            return pw

        attempts += 1

        print(
            f"Incorrect password. "
            f"{MAX_ATTEMPTS - attempts} attempts remaining."
        )

    return None

        




