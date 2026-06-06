from auth import create_master_passwd, hash_pw, verify_pw
from crypto import derive_salt, derive_key, encrypt, decrypt
from database import create_db, create_tables, master_pw_exists, add_master_pw, get_master_auth, add_vault_entry, get_vault_entries

link = create_db()

#logged in user
if (master_pw_exists):
    mp = input("Enter master password:")
    hash_mp = hash_pw(mp)
    if verify_pw(mp, hash_mp):
        print("Welcome, you have successfully logged in")
    else:
        print("Password incorrect")

else:
    create_tables(link)
    add_master_pw(link, )

    

