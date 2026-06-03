import sqlite3 as sql


def create_db():
    con = sql.connect("storage.db")
    return con


def create_tables(con):
    cur = con.cursor()

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

    cur.execute(q1)
    cur.execute(q2)

    con.commit()

