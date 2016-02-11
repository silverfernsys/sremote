#!/usr/bin/env python
import json
import tornado.websocket
from models.user import User
from models.token import Token

class WSHandler(tornado.websocket.WebSocketHandler):
    connections = []

    @tornado.web.addslash
    def open(self):
        auth_token = self.request.headers.get('authorization')
        token = Token.tokens().get(token=auth_token)
        if token and token.user:
            WSHandler.connections.append(self)
        else:
            self.close()
      
    def on_message(self, message):
        auth_token = self.request.headers.get('authorization')
        token = Token.tokens().get(token=auth_token)
        if token and token.user:
            data = json.loads(message)
            if data['msg'] == 'update':
                self.write_message(json.dumps({'msg':'updated'}))
 
    def on_close(self):
        if self in WSHandler.connections:
            WSHandler.connections.remove(self)

    def check_origin(self, origin):
        return True