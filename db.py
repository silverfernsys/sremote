#!/usr/bin/env python
import sqlite3
import time
import os
import binascii

class Db():
    _instance = None

    @classmethod
    def instance(self, path=None):
        if path != None:
            Db._instance = Db(path)
        return Db._instance

    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self._create_tables()

    # These are helper functions for server.py to interact with the sqlite database.
    # Check if table exists.
    # http://stackoverflow.com/questions/1601151/how-do-i-check-in-sqlite-whether-a-table-exists
    def _table_exists(self, tablename):
        cur = self.conn.cursor()
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % tablename
        cur.execute(query)
        if cur.fetchone() is None:
            return False
        return True

    def _create_tables(self):
        cur = self.conn.cursor()
        if self._table_exists('user') is False:
            create_user_table = """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT, password TEXT, admin INTEGER, created TIMESTAMP, UNIQUE(username));"""
            cur.execute(create_user_table)
        if self._table_exists('token') is False:
            create_token_table = """CREATE TABLE token (id INTEGER PRIMARY KEY AUTOINCREMENT,
                userid INTEGER, token TEXT, created TIMESTAMP, UNIQUE(token));"""
            cur.execute(create_token_table)
        self.conn.commit()

    def drop_tables(self):
        cur = self.conn.cursor()
        if self._table_exists('user') is True:
            drop_user_table = """DROP TABLE user;"""
            cur.execute(drop_user_table)
        if self._table_exists('token') is True:
            drop_token_table = """DROP TABLE token;"""
            cur.execute(drop_token_table)
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

    def authenticate_user(self, username, password):
        user = self.get_user(username)
        if user:
            if password == user[2]:
                return True
            else:
                return False
        else:
            return False

    def is_admin(self, username):
        user = self.get_user(username)
        if user:
            if user[3] == 1:
                return True
            else:
                return False
        else:
            return False

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

    # This function creates a token for a user if none exists,
    # then returns that user's token.
    def get_token(self, username):
        user = self.get_user(username)
        cur = self.conn.cursor()
        values = (user[0], ) # user.id
        cur.execute('SELECT * FROM token WHERE userid=?;', values)
        token_data = cur.fetchone()
        if token_data != None:
            # Return an existing token
            return token_data[2]
        else:
            return None

    def create_token(self, username):
        existing_token = self.get_token(username)
        if existing_token is None:
            cur = self.conn.cursor()
            # https://github.com/tomchristie/django-rest-framework/blob/master/rest_framework/authtoken/models.py
            token = binascii.hexlify(os.urandom(20)).decode()
            user = self.get_user(username)
            values = (None, user[0], token, time.time())
            cur = self.conn.cursor()
            cur.execute('INSERT INTO token VALUES (?,?,?,?)', values)
            self.conn.commit()
            return True
        else:
            return False

    def token_count(self):
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM token;')
        return cur.fetchone()[0]

    def list_tokens(self):
        cur = self.conn.cursor()
        join = """
        SELECT user.username, token.token, token.created FROM user INNER JOIN token ON token.userid = user.id ORDER BY user.username, token.created;
        """
        return cur.execute(join)

    def get_user_with_token(self, token):
        cur = self.conn.cursor()
        cur.execute('SELECT userid FROM token WHERE token=?', (token,))
        token_data = cur.fetchone()
        if token_data:
            cur.execute('SELECT * FROM user WHERE id=?', (token_data[0],))
            return cur.fetchone()
        else:
            return None

    # Deletes a token if it exists. Returns true if there was a token to delete.
    # Returns false if there was no token to delete.
    def delete_token(self, username):
        token = self.get_token(username)
        if token is None:
            return False
        else:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM token WHERE token=?', (token,))
            self.conn.commit()
            return True

import unittest
import tempfile

class DbTest(unittest.TestCase):
    def setUp(self):
        self.temp_path = tempfile.mktemp()
        Db.instance(self.temp_path)

    def tearDown(self):
        os.remove(self.temp_path)

    def testDb(self):
        # Test users
        Db.instance().insert_user('info@example.com', 'asdf', 1)
        Db.instance().insert_user('info1@example.com', 'asdf', 0)
        Db.instance().insert_user('info2@example.com', 'qwer', 0)
        self.assertEqual(Db.instance().user_count(), 3, 'There are 3 users')
        self.assertEqual(Db.instance().user_exists('info@example.com'), True, 'info@example.com exists')
        self.assertEqual(Db.instance().get_user('info1@example.com')[1], 'info1@example.com', 'emails are equal')
        Db.instance().delete_user('info2@example.com')
        self.assertEqual(Db.instance().user_count(), 2, 'There are now 2 users')
        self.assertEqual(Db.instance().user_exists('info2@example.com'), False, 'info2@example.com does not exist')
        
        # Test tokens
        self.assertEqual(Db.instance().get_token('info@example.com'), None, 'no token exists')
        self.assertEqual(Db.instance().create_token('info@example.com'), True, 'successfully created token')
        self.assertEqual(Db.instance().create_token('info@example.com'), False, 'token already exists')
        self.assertEqual(Db.instance().get_token('info@example.com'), Db.instance().get_token('info@example.com'), 'tokens are equal')
        self.assertEqual(Db.instance().token_count(), 1, '1 token')
        self.assertEqual(Db.instance().delete_token('info@example.com'), True, 'deleted token')
        self.assertEqual(Db.instance().delete_token('info@example.com'), False, 'no token to delete')
        self.assertEqual(Db.instance().token_count(), 0, '0 tokens')

        Db.instance().create_token('info@example.com')
        token = Db.instance().get_token('info@example.com')
        self.assertEqual(Db.instance().get_user_with_token(token)[1], 'info@example.com', 'user emails are equal')

        # Test creation and cleanup 
        self.assertEqual(Db.instance()._table_exists('user'), True, 'user table exists')
        self.assertEqual(Db.instance()._table_exists('token'), True, 'token table exists')
        Db.instance().drop_tables()
        self.assertEqual(Db.instance()._table_exists('user'), False, 'user table does not exist')
        self.assertEqual(Db.instance()._table_exists('token'), False, 'token table does not exist')

if __name__ == '__main__':
    unittest.main()