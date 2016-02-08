#!/usr/bin/env python

import tornado
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application
from sremote.ws import WSHandler

class WebSocketTestCase(AsyncHTTPTestCase):
    def get_app(self):
        app = Application([
            (r'/ws/', WSHandler),
        ])
        return app

    @tornado.testing.gen_test
    def test_wshandler(self):
        # self.get_http_port() gives us the port of the running test server.
        ws_url = 'ws://localhost:' + str(self.get_http_port()) + '/ws/'
        ws_client = yield tornado.websocket.websocket_connect(ws_url)

        # Now we can run a test on the WebSocket.
        ws_client.write_message("Hi, I'm sending a message to the server.")
        response = yield ws_client.read_message()
        self.assertEqual(response, None, "No response from server because authorization not provided.")
        # self.assertEqual(response, "Hi client! This is a response from the server.")