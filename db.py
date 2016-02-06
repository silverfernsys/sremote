#!/usr/bin/env python
import sqlite3
import time
import os

class Db():
    _instance = None

    @classmethod
    def instance(self, path=None):
        if path != None:
            Db._instance = Db(path)
        return Db._instance

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self._create_tables(self.conn)

    # These are helper functions for server.py to interact with the sqlite database.
    # Check if table exists.
    # http://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
    def _table_exists(self, cur, tablename):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
        cur.execute(query)
        if cur.fetchone() is None:
            return False
        return True

    def _create_tables(self, conn):
        cur = conn.cursor()
        if self._table_exists(cur, 'user') is False:
            create_user_table = """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT, password TEXT, admin INTEGER, created TIMESTAMP, UNIQUE(username));"""
            cur.execute(create_user_table)
            conn.commit()

    def drop_tables(self):
        cur = self.conn.cursor()
        if self._table_exists(cur, 'user') is True:
            drop_user_table = """DROP TABLE user;"""
            cur.execute(drop_user_table)
            self.conn.commit()

    def insert_user(self, username, password, admin):
        values = (None, username, password, admin, time.time())
        cur = self.conn.cursor()
        cur.execute('INSERT INTO user VALUES (?,?,?,?,?)', values)
        self.conn.commit()

    def list_users(self):
        cur = self.conn.cursor()
        return cur.execute('SELECT * FROM user ORDER BY username, created;')

    def user_count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM user;')
        return cur.fetchone()[0]

    def get_user(self, username):
        t = (username,)
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM user WHERE username=?', t)
        return cur.fetchone()

    def user_exists(self, username):
        t = (username,)
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM user WHERE username=?', t)
        if cur.fetchone() is None:
            return False
        return True

    def delete_user(self, username):
        t = (username,)
        cur = self.conn.cursor()
        cur.execute('DELETE FROM user WHERE username=?', t)
        self.conn.commit()

import unittest
import tempfile

class DbTest(unittest.TestCase):
    def setUp(self):
        self.temp_path = tempfile.mktemp()
        Db.instance(self.temp_path)

    def tearDown(self):
        os.remove(self.temp_path)

    def testUser(self):
        Db.instance().insert_user('info@example.com', 'asdf', 1)
        Db.instance().insert_user('info1@example.com', 'asdf', 0)
        Db.instance().insert_user('info2@example.com', 'qwer', 0)
        self.assertEqual(Db.instance().user_count(), 3, 'There are 3 users')
        self.assertEqual(Db.instance().user_exists('info@example.com'), True, 'info@example.com exists')
        self.assertEqual(Db.instance().get_user('info1@example.com')[1], 'info1@example.com', 'emails are equal')
        Db.instance().delete_user('info2@example.com')
        self.assertEqual(Db.instance().user_count(), 2, 'There are now 2 users')
        self.assertEqual(Db.instance().user_exists('info2@example.com'), False, 'info2@example.com does not exist')

if __name__ == '__main__':
    unittest.main()