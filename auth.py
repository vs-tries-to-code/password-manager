import bcrypt

def create_master_passwd():
    master_pw = input("Enter master password: ")
    mp2 = input("Confirm password: ")
    if master_pw == mp2:
        print("Master password set")
        return master_pw

    print("Passwords do not match, enter password again")
    return None

def hash_pw(passwd):
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt())

def verify_pw(passwd, stored_hash):
    pw_bytes = passwd.encode('utf-8')
    return bcrypt.checkpw(pw_bytes, stored_hash)
        




