import bcrypt 
import cryptography
def create_master_passwd():
    master_pw = input("Enter master password: ")
    mp2 = input("Confirm password: ")
    if (master_pw == mp2):
        print("Master password set!")
        return master_pw
    else:
        print("Passwords do not match, enter password again")
        return 0

def hash_pw(passwd):
    pw_bytes = passwd.encode('utf-8')
    encr_salt = bcrypt.gensalt()
    hash_pw  = bcrypt.hashpw(pw_bytes, encr_salt)
    return hash_pw, encr_saltsalt

def verify_pw(passwd, hash_pw):
    pw_bytes = passwd.encode('utf-8')
    encr_salt = bcrypt.gensalt()
    hash_passwd  = bcrypt.hashpw(pw_bytes, encr_salt)
    if (hash_passwd == hash_pw):
        print("Authentication successful")
        return 1
    else:
        print("Authentication unsuccessful")
        return 0
        




