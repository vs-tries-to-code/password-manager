import sqlite3 as sql

def create_db_connection():
    q = """ CREATE DATABASE IF NOT EXISTS storage.db"""
    return sql.connect("storage.db")


def create_tables(con):
    cur = con.cursor()

    q1 = """
    CREATE TABLE IF NOT EXISTS master_auth (
        id INTEGER PRIMARY KEY,
        password_hash BLOB NOT NULL,
        encryption_salt BLOB NOT NULL, 
        vault_key_encryp BLOB NOT NULL
    );
    """

    q2 = """
    CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        password BLOB NOT NULL
    );
    """

    cur.execute(q1)
    cur.execute(q2)
    con.commit()


def master_pw_exists(con):
    cur = con.cursor()
    q = "SELECT COUNT(*) FROM master_auth;"
    try:
        cur.execute(q)
        count = cur.fetchone()[0]
        return count > 0
    except sql.OperationalError:
        return False
    


def get_master_auth(con):
    cur = con.cursor()
    q = "SELECT password_hash, encryption_salt, vault_key_encryp FROM master_auth WHERE id = 1 LIMIT 1;"
    cur.execute(q)
    return cur.fetchone()


def add_master_pw(con, hash_value, salt, vault_key_encryp):
    cur = con.cursor()
    q = "INSERT OR REPLACE INTO master_auth (id, password_hash, encryption_salt, vault_key_encryp) VALUES (1, ?, ?, ?);"
    cur.execute(q, (hash_value, salt, vault_key_encryp))
    con.commit()
    print("Master Password set successfully")

def add_vault_entry(con, website, username, password_ciphertext):
    cur = con.cursor()
    q = "INSERT INTO vault (website, username, password) VALUES (?, ?, ?);"
    cur.execute(q, (website, username, password_ciphertext))
    con.commit()


def get_vault_entries(con, website):
    cur = con.cursor()
    q = f"SELECT website, username, password FROM vault WHERE website = ? ORDER BY id;"
    cur.execute(q, (website,))
    return cur.fetchone()

def update_entry(con, website, pw_cipher):
    cur = con.cursor()
    q = f"UPDATE vault SET password = ? WHERE website = ?;"
    cur.execute(q, (pw_cipher, website))
    con.commit()
    print("Updation successful")
   
def list_entries(con):
    cur = con.cursor()
    q = f"SELECT website, username FROM vault ORDER BY id;"
    cur.execute(q)
    return cur.fetchall()
    