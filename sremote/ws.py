#!/usr/bin/env python
import json
import tornado.websocket
from models.db import Db

class WSHandler(tornado.websocket.WebSocketHandler):
    connections = []

    # def __init__(self, application, request, **kwargs):
    #     super(WSHandler, self).__init__(application, request, **kwargs)
    #     print("WSHandler")

    # def __del__(self):
    #     print("WSHandler.__del__")
    @tornado.web.addslash
    def open(self):
        token = self.request.headers.get('authorization')
        user = Db.instance().get_user_with_token(token)
        if user:
            WSHandler.connections.append(self)
        else:
            self.close()
      
    def on_message(self, message):
        token = self.request.headers.get('authorization')
        user = Db.instance().get_user_with_token(token)
        if user:
            data = json.loads(message)
            if data['msg'] == 'update':
                self.write_message(json.dumps({'msg':'updated'}))
 
    def on_close(self):
        if self in WSHandler.connections:
            WSHandler.connections.remove(self)

    def check_origin(self, origin):
        return True