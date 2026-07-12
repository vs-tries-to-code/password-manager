from auth import create_master_passwd, hash_pw, verify_pw, login
from crypto import derive_salt, derive_key, encrypt, decrypt
from database import create_db_connection, create_tables, master_pw_exists, add_master_pw, get_master_auth, add_vault_entry, get_vault_entries, update_entry
from getpass import getpass

link = create_db_connection()

def menu(key):
    while True:
        print("1. Add entry")
        print("2. Edit password")
        print("3. Fetch password")
        print("4. Update master password")
        print("5. Exit")
        c = int(input("Enter choice"))
        if c==1:
            website = input("Enter website name: ")
            username = input("Enter username: ")
            pw = getpass("Enter password: ")
            ciphertext = encrypt(pw, key)
            add_vault_entry(link, website, username, ciphertext)
            print("Entry added successfully!")
        elif c==2:
            website = input("Enter website name: ")
            pw = getpass("Enter new password")
            ciphertext = encrypt(pw, key)
            update_entry(link, website, ciphertext)
        elif c==3:
            website = input("Enter website name: ")
            web, uname, pw_cipher = get_vault_entries(link, website)
            d_cipher = decrypt(pw_cipher, key)
            print("Password : ", d_cipher)
        elif c==4:
            hashed_pw, encryption_salt = get_master_auth(link)
            k = login(hashed_pw, stored_salt)
            if k is not None:
                new_mp = set_new_mp()
                hashed_pw = hash_pw(new_mp)
                salt = derive_salt()
                add_master_pw(link, hashed_pw, salt)
            else:
                print("Too many attempts, password change unsuccessful")
                exit()

        elif c==5:
            print("Exiting program")
            exit()
        else:
            print("Invalid choice.\n Press either 1,2,3 or 4")

#user with master password
if master_pw_exists(link):
    pw_hash, encryption_salt = get_master_auth(link)
    k = login(pw_hash, encryption_salt)
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
        salt = derive_salt()
        add_master_pw(link, hashed_pw, salt)
        k = login(hashed_pw, salt)
        if k is not None:
            menu(k)
        else:
            print("Too many attempts, login unsuccessful")
            exit()
                
    

