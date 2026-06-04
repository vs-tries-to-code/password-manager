import sqlite3 as sql


def create_db():
    con = sql.connect("storage.db")
    return con


def create_tables(con):
    cur = con.cursor()

    q = "USE storage.db;"

    q1 = """
    CREATE TABLE IF NOT EXISTS master_auth (
        id INTEGER PRIMARY KEY,
        password_hash BLOB NOT NULL,
        encryption_salt BLOB NOT NULL
    );
    """

    q2 = """
    CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY,
        website TEXT NOT NULL,
        username TEXT NOT NULL,
        password BLOB NOT NULL
    );
    """
    cur.execute(q)
    cur.execute(q1)
    cur.execute(q2)

    con.commit()

def master_pw_exists(con):
    cur = con.cursor()
    q = "SELECT * FROM master_auth;"
    cur.execute(q)
    
    row = cur.fetchone()

    if row is not None:
        return True
    else:
        return False

def add_master_pw(con, hash, salt):
    cur = con.cursor()
    p = f"iNSERT INTO master_auth VALUES (1, {hash}, {salt});"
    cur.execute(p)
    con.commit()
    