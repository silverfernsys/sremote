#!/usr/bin/env python
import unittest
import time
from sremote.models.database import Database, DatabaseManager

class UserTest(unittest.TestCase):
    def setUp(self):
    	DatabaseManager.add('default', ':memory:')

    def tearDown(self):
        DatabaseManager.remove('default')

    def test_user(self):
    	# I need some way of deferring creation of UserManager
    	# until DatabaseManager has been instantiated.
    	# So that's why the import is inside this function, so
    	# that it's called AFTER I've had a chance to call
    	# DatabaseManager.add('default', ':memory:')
    	from sremote.models.user import User
    	user_0 = User('jack', 'asdf', True)
    	self.assertEqual(user_0.username, 'jack')
    	self.assertEqual(user_0.password, 'asdf')
    	self.assertTrue(user_0.admin)
    	self.assertEqual(user_0.id, None)
    	self.assertEqual(user_0.created, None)
    	self.assertEqual(User.users.count(), 0, 'No users in database.')
    	user_0.save()
    	self.assertEqual(User.users.count(), 1, '1 user in database.')
    	self.assertEqual(user_0.id, 1, 'User has id=1.')
    	self.assertLess(user_0.created, time.time(), 'User was created before now.')
    	user_0.username = 'jill'
    	user_0.admin = False
    	user_0.save()

    	# Now drop into sql to ensure that we really saved the object's username
    	db = DatabaseManager.instance('default')
    	select_user_query = 'SELECT * FROM user WHERE id=?;'
        select_result = db.query(select_user_query, (user_0.id,)).next()
        self.assertEqual(select_result['username'], 'jill')
        self.assertEqual(select_result['admin'], 0)

        # Now delete the object
        user_0.delete()
        self.assertEqual(User.users.count(), 0, 'No more users in database.')
        self.assertEqual(user_0.id, None, 'id is None')
        self.assertEqual(user_0.created, None, 'created is None')
        