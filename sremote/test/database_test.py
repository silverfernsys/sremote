import unittest
import tempfile
import os
import time
from sremote.models.database import Database, DatabaseManager

class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(':memory:')

    def tearDown(self):
        pass

    def testDatabaseManager(self):
        DatabaseManager.add('default', ':memory:')
        db = DatabaseManager.instance('default')
        self.assertTrue(db != None, 'Database exists.')
        DatabaseManager.remove('default')
        self.assertRaises(KeyError, DatabaseManager.instance, 'DatabaseManager raises KeyError when no db exists.')

    def testDatabase(self):
        self.assertEqual(len(self.db.get_table_names()), 0, "no names in get_table_names()")
        create_user_table_query = """CREATE TABLE user (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                username TEXT, password TEXT, admin INTEGER, created TIMESTAMP, UNIQUE(username));"""
        self.db.query(create_user_table_query)
        table_names = self.db.get_table_names()
        self.assertTrue('user' in table_names, "'user' in get_table_names()")
        self.assertTrue(self.db.table_exists('user'), "'user' table exists.")
        self.assertFalse(self.db.table_exists('random'), "'random' table does not exist.")
        
        # Insert users and count the resulting entries
        create_user_query = 'INSERT INTO user VALUES (?,?,?,?,?);'

        user_values = [
            (None, 'john', 'asdf', 1, time.time()),
            (None, 'jill', 'asdf', 1, time.time()),
            (None, 'jack', 'zxcv', 1, time.time())
        ]

        for value in user_values:
            insert_result = self.db.query(create_user_query, value)
        count_result = self.db.query('SELECT COUNT(*) FROM user;')
        self.assertEqual(count_result.nextresult()['COUNT(*)'], 3, '3 users in table')

        # Delete a user and count the resulting entries
        delete_user_query = 'DELETE FROM user WHERE username=?;'
        self.db.query(delete_user_query, ('john',))
        self.assertEqual(self.db.query('SELECT COUNT(*) FROM user;').nextresult()['COUNT(*)'], 2, '2 users in table')

        # Select a user and inspect it's values
        select_user_query = 'SELECT * FROM user WHERE username=?;'
        select_result = self.db.query(select_user_query, ('jill',)).nextresult()
        self.assertEqual(select_result['username'], 'jill')
        self.assertEqual(select_result['admin'], 1)
        self.assertEqual(select_result['password'], 'asdf')

        # Update a user and inspect it's values
        update_user_query = 'UPDATE user SET username=?, admin=? WHERE id=?;'
        self.db.query(update_user_query, ('jane', 0, 2))
        select_user_query = 'SELECT * FROM user WHERE username=?;'
        select_result = self.db.query(select_user_query, ('jane',)).nextresult()
        self.assertEqual(select_result['username'], 'jane')
        self.assertEqual(select_result['admin'], 0)
        self.assertEqual(select_result['password'], 'asdf')

        drop_table_query = 'DROP TABLE user;'
        self.db.query(drop_table_query)
        self.assertFalse(self.db.table_exists('user'), "'user' table has been dropped.")
        
