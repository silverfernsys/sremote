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
    	self.assertEqual(User.users().count(), 0, 'No users in database.')
    	user_0.save()
    	self.assertEqual(User.users().count(), 1, '1 user in database.')
    	self.assertEqual(user_0.id, 1, 'User has id=1.')
    	self.assertLess(user_0.created, time.time(), 'User was created before now.')
    	user_0.username = 'jill'
    	user_0.admin = False
    	user_0.save()

    	# Now drop into sql to ensure that we really saved the object's username
    	db = DatabaseManager.instance('default')
    	select_user_query = 'SELECT * FROM user WHERE id=?;'
        select_result = db.query(select_user_query, (user_0.id,)).nextresult()
        self.assertEqual(select_result['username'], 'jill')
        self.assertEqual(select_result['admin'], 0)

        # Now test the UserManager.get() method:
        user_0_1 = User.users().get(id=user_0.id)
        user_0_2 = User.users().get(username=user_0.username)
        user_0_3 = User.users().get(id=user_0.id, username=user_0.username)
        self.assertEqual(user_0.username, user_0_1.username, 'usernames equal')
        self.assertEqual(user_0_1.username, user_0_2.username, 'usernames equal')
        self.assertEqual(user_0_1.username, user_0_3.username, 'usernames equal')

        self.assertEqual(user_0.id, user_0_1.id, 'ids equal')
        self.assertEqual(user_0_1.id, user_0_2.id, 'ids equal')
        self.assertEqual(user_0_1.id, user_0_3.id, 'ids equal')

        self.assertEqual(user_0.admin, user_0_1.admin, 'admin equal')
        self.assertEqual(user_0_1.admin, user_0_2.admin, 'admin equal')
        self.assertEqual(user_0_1.admin, user_0_3.admin, 'admin equal')

        self.assertTrue(user_0.authenticate('asdf'), 'User authenticates.')
        self.assertFalse(user_0.authenticate('qwer'), 'User does not authenticate.')

        # Now delete the object
        user_0.delete()
        self.assertEqual(User.users().count(), 0, 'No more users in database.')
        self.assertEqual(user_0.id, None, 'id is None')
        self.assertEqual(user_0.created, None, 'created is None')

        creation_count = 10
        for i in range(creation_count):
            user = User('user%s' % i, 'asdf', True)
            user.save()

        self.assertEqual(User.users().count(), creation_count, 'count() == creation_count')

        all_users = User.users().all()
        self.assertEqual(creation_count, len(all_users), 'len == creation_count')

        user_1 = User('jill', 'qwer', True)
        self.assertFalse(user_1.authenticate('qwer'), 'User does not authenticate because it has not been saved.')
        self.assertFalse(user_1.authenticate('asdf'), 'User does not authenticate because it has not been saved.')
        