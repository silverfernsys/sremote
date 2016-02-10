#!/usr/bin/env python
# Adapted from https://github.com/tornadoweb/tornado/blob/master/tornado/test/httpclient_test.py

import json
import os
import tempfile
import time

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler, url

from sremote.http import HTTPVersionHandler, HTTPStatusHandler, HTTPTokenHandler
from sremote.models.database import DatabaseManager 
from sremote.procinfo import ProcInfo

class HTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(HTTPTestCase, self).setUp()
        DatabaseManager.add('default', ':memory:')

        from sremote.models.user import User, UserManager
        from sremote.models.token import Token, TokenManager

        User.users = UserManager()
        Token.tokens = TokenManager()

        self.username_0 = 'info@example.com'
        self.password_0 = 'asdfasdf'
        self.username_1 = 'info1@example.com'
        self.password_1 = 'qwerqwer'

        self.user_0 = User(self.username_0, self.password_0, True)
        self.user_0.save()

        self.user_1 = User(self.username_1, self.password_1, True)
        self.user_1.save()

        self.token_0 = Token(user=self.user_0)
        self.token_0.save()

        self.token_1 = Token(user=self.user_1)
        self.token_1.save()

    def tearDown(self):
        DatabaseManager.remove('default')
        ProcInfo.purge()

    def get_app(self):
        return Application([
            url(r'/', HTTPVersionHandler),
            url(r'/status/', HTTPStatusHandler),
            url(r'/token/', HTTPTokenHandler),
        ])

    def test_http_handler(self):
        response = self.fetch('/', method='GET')
        response_data = json.loads(response.body)
        self.assertTrue('version' in response_data)
        self.assertEqual(response.code, 200)

    def test_http_token_handler(self):
        headers = {'username':self.username_0, 'password':self.password_0}
    	response = self.fetch('/token/', method='GET', headers=headers)
        response_data = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(self.token_0.token, response_data['token'])

    def test_http_status_handler(self):
        ProcInfo('proc_0', 'group_0', 1, 20, 'RUNNING', time.time())
        ProcInfo('proc_1', 'group_1', 2, 0, 'STOPPED', time.time())
        
        # Update ProcInfo 3 times.
        num_updates = 3
        for i in range(num_updates):
            ProcInfo.updateall()

        headers = {'authorization': self.token_0.token}
        response = self.fetch('/status/', method='GET', headers=headers)
        response_data = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertTrue('processes' in response_data)
        self.assertEqual(len(response_data['processes'][0]['cpu']), num_updates, "cpu length is %s" % num_updates)
        self.assertEqual(len(response_data['processes'][0]['mem']), num_updates, "mem length is %s" % num_updates)
