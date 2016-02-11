#!/usr/bin/env python
import unittest
import time
from sremote.models.database import Database, DatabaseManager
from sremote.models.user import User, UserManager
from sremote.models.token import Token, TokenManager

class TokenTest(unittest.TestCase):
    def setUp(self):
    	DatabaseManager.add('default', ':memory:')

    def tearDown(self):
        DatabaseManager.remove('default')

    def test_token(self):
    	
        # The reason we're creating a new UserManager() here is because
        # there was a previous UserManager() instance created in another
        # test that was connected to a different database. So, we create
        # a new UserManager() that connects to the database we've created
        # in this test.
        User._users = UserManager()
        Token._tokens = TokenManager()

    	user_0 = User('jim', 'asdf', True)
    	user_0.save()

        user_1 = User('jane', 'qwer', False)
        user_1.save()

        token_0 = Token(user_0)
        token_0.save()

        with self.assertRaises(ValueError):
            token_0.save()

        self.assertEqual(token_0.id, 1, 'id is 1')

        token_0_1 = Token.tokens().get_token_for_user(user_0)
        self.assertEqual(token_0.id, token_0_1.id, 'ids are equal')
        self.assertEqual(token_0.user, token_0_1.user, 'users are equal')
        self.assertEqual(token_0.token, token_0_1.token, 'tokens are equal')
        self.assertEqual(token_0.created, token_0_1.created, 'created are equal')

        token_1 = Token(user_1)
        token_1.save()
        self.assertEqual(token_1.id, 2, 'id is 2')
        self.assertEqual(Token.tokens().count(), 2, '2 tokens saved')

        token_2 = Token(user_0)
        with self.assertRaises(ValueError):
            token_2.save()

        self.assertEqual(Token.tokens().count(), 2, 'still 2 tokens saved')
        self.assertEqual(len(Token.tokens().all()), 2, 'len of all is 2.')

        token_1.delete()
        self.assertEqual(token_1.id, None, 'token has no id')
        self.assertEqual(token_1.created, None, 'token has no created')
        self.assertEqual(Token.tokens().count(), 1, '1 token saved')
        token_1.delete()
        self.assertEqual(Token.tokens().count(), 1, 'still 1 token saved')


