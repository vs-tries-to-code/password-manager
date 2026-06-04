import bcrypt 
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
    hash_pw  = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    return hash_pw

def verify_pw(passwd, hash_pw):
    pw_bytes = passwd.encode('utf-8')
    hash_passwd  = bcrypt.hashpw(pw_bytes, bcrypt.gensalt())
    if (hash_passwd == hash_pw):
        print("Authentication successful")
        return 1
    else:
        print("Authentication unsuccessful")
        return 0
        




