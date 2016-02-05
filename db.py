#!/usr/bin/env python
import sqlite3
import time

def connect(path):
    conn = sqlite3.connect(path)
    return conn

# These are helper functions for server.py to interact with the sqlite database.
# Check if table exists.
# http://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
def table_exists(cur, tablename):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
    cur.execute(query)
    if cur.fetchone() is None:
        return False
    return True

def create_tables(conn, cur):
    # user
    if table_exists(cur, 'user') is False:
        print("Creating 'users' table...")
        create_user_table = """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT, password TEXT, admin INTEGER, created TIMESTAMP, UNIQUE(username));"""
        cur.execute(create_user_table)
        conn.commit()
    # else:
    #     print("Table 'users' exists.")

def drop_tables(conn, cur):
    if table_exists(cur, 'user') is True:
        drop_user_table = """DROP TABLE user;"""
        cur.execute(drop_user_table)
        conn.commit()
    # else:
    #     print("Table 'users' does not exist.")

def insert_user(conn, cur, username, password, admin):
    values = (None, username, password, admin, time.time())
    cur.execute('INSERT INTO user VALUES (?,?,?,?,?)', values)
    conn.commit()

def list_users(conn, cur):
    return cur.execute('SELECT * FROM user ORDER BY username, created;')

def user_count(conn, cur):
    cur.execute('SELECT COUNT(*) FROM user;')
    return cur.fetchone()[0]

def get_user(conn, cur, username):
    t = (username,)
    cur.execute('SELECT * FROM user WHERE username=?', t)
    return cur.fetchone()

def user_exists(conn, cur, username):
    t = (username,)
    cur.execute('SELECT * FROM user WHERE username=?', t)
    if cur.fetchone() is None:
        return False
    return True

def delete_user(conn, cur, username):
    t = (username,)
    cur.execute('DELETE FROM user WHERE username=?', t)
    conn.commit()

def main():
    conn = sqlite3.connect('etc/db.sqlite')
    cur = conn.cursor()
    # create_tables(conn, cur)
    # insert_user(conn, cur, 'info@example.com', 'secret')
    # list_users(conn, cur)
    # print(user_exists(conn, cur, 'info@example.com'))
    # delete_user(conn, cur, 'info@example.com')
    # list_users(conn, cur)
    drop_tables(conn, cur)


if __name__ == '__main__':
    main()