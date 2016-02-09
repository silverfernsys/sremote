#!/usr/bin/env python
# Adapted from https://github.com/tornadoweb/tornado/blob/master/tornado/test/httpclient_test.py

import json
import os
import tempfile

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler, url

from sremote.http import HTTPHandler, HTTPStatusHandler, HTTPTokenHandler
from sremote.models.db import Db

class HTTPTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super(HTTPTestCase, self).setUp()
        self.temp_path = tempfile.mktemp()
        Db.instance(self.temp_path)
        self.username_0 = 'info@example.com'
        self.password_0 = 'asdf'
        self.username_1 = 'info1@example.com'
        self.password_1 = 'asdf'
        Db.instance().insert_user(self.username_0, self.password_0, 1)
        Db.instance().insert_user(self.username_1, self.password_1, 0)
        Db.instance().create_token(self.username_0)
        Db.instance().create_token(self.username_1)
        self.token_0 = Db.instance().get_token(self.username_0)
        self.token_1 = Db.instance().get_token(self.username_1)

    def tearDown(self):
        os.remove(self.temp_path)

    def get_app(self):
        return Application([
            url(r'/', HTTPHandler),
            url(r'/status/', HTTPStatusHandler),
            url(r'/token/', HTTPTokenHandler),
        ])

    def test_http_handler(self):
        response = self.fetch('/', method='GET')
        self.assertEqual(response.code, 200)

    def test_http_token_handler(self):
        headers = {'username':self.username_0, 'password':self.password_0}
    	response = self.fetch('/token/', method='GET', headers=headers)
        response_data = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertEqual(self.token_0, response_data['token'])

    def test_http_status_handler(self):
        headers = {'authorization': self.token_0}
        response = self.fetch('/status/', method='GET', headers=headers)
        response_data = json.loads(response.body)
        self.assertEqual(response.code, 200)
        self.assertTrue('processes' in response_data)
        # print(response.code)
        # print(response.body)

    # def test_patch_receives_payload(self):
    #     body = b"some patch data"
    #     response = self.fetch("/", method='PATCH', body=body)
    #     self.assertEqual(response.code, 200)
    #     self.assertEqual(response.body, body)
