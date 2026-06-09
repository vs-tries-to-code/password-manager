from auth import create_master_passwd, hash_pw, verify_pw, login
from crypto import derive_salt, derive_key, encrypt, decrypt
from database import create_db, create_tables, master_pw_exists, add_master_pw, get_master_auth, add_vault_entry, get_vault_entries
from getpass import getpass

link = create_db()

def menu(key):
    while True:
        print("1. Add entry")
        print("2. Edit password")
        print("3. Fetch password")
        print("4. Exit")
        c = int(input("Enter choice"))
        if c==1:
            website = input("Enter website name: ")
            username = input("Enter username: ")
            pw = getpass("Enter password: ")
            ciphertext = encrypt(pw, key)
            add_vault_entry(link, website, username, ciphertext)
            print("Entry added successfully!")
        elif c==2:
            pass
        elif c==3:
            website = input("Enter website name: ")
            web, uname, pw_cipher = get_vault_entries(link, website)
            d_cipher = decrypt(pw_cipher, key)
            print("Password : ", d_cipher)
        elif c==4:
            exit()
        else:
            print("Invalid choice.\n Press either 1,2,3 or 4")

#user with master password
if master_pw_exists():
    stored_salt, master_pw = get_master_auth(link)
    k = login(stored_salt)
    if k is not None:
        menu(k)
    else:
        print("Too many attempts, login unsuccessful")
        exit()


else:
    #new user
    create_tables(link)
    pw = create_master_passwd()
    if pw is not None:
        hashed_pw = hash_pw(pw)
        if verify_pw(pw, hashed_pw):
            salt = derive_salt()
            derive_key(pw, salt)
            add_master_pw(link, hashed_pw, salt)


    

