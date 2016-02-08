#!/usr/bin/env python
# Adapted from https://github.com/tornadoweb/tornado/blob/master/tornado/test/httpclient_test.py

from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler, url
from sremote.http import HTTPHandler, HTTPStatusHandler, HTTPTokenHandler

class HTTPTestCase(AsyncHTTPTestCase):
    def get_app(self):
        return Application([
            url(r'/', HTTPHandler),
            url(r'/status/', HTTPStatusHandler),
            url(r'/token/', HTTPTokenHandler),
        ], gzip=True)

    def test_http_handler(self):
        response = self.fetch('/', method='GET')
        self.assertEqual(response.code, 200)

    def test_http_status_handler(self):
    	pass
    	# response = self.fetch('/status/', method='GET', headers=headers)

    # def test_patch_receives_payload(self):
    #     body = b"some patch data"
    #     response = self.fetch("/", method='PATCH', body=body)
    #     self.assertEqual(response.code, 200)
    #     self.assertEqual(response.body, body)
