import unittest
import tempfile
import os
from sremote.models.db import Db

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
        self.assertEqual(Db.instance().get_user_with_token(token)['username'], 'info@example.com', 'user emails are equal')

        # Test creation and cleanup 
        self.assertEqual(Db.instance()._table_exists('user'), True, 'user table exists')
        self.assertEqual(Db.instance()._table_exists('token'), True, 'token table exists')
        Db.instance().drop_tables()
        self.assertEqual(Db.instance()._table_exists('user'), False, 'user table does not exist')
        self.assertEqual(Db.instance()._table_exists('token'), False, 'token table does not exist')
