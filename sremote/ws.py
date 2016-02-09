#!/usr/bin/env python
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
        print('new connection')
        token = self.request.headers.get('authorization')
        print('token: %s' % token)
        try:
            user = Db.instance().get_user_with_token(token)
            if user:
                print('FOUND USER')
                WSHandler.connections.append(self)
            else:
                print('CLOSING CONNECTION')
                self.close()
        except Exception as e:
            self.close()
      
    def on_message(self, message):
        try:
            token = self.request.headers.get('authorization')
            user = Db.instance().get_user_with_token(token)
            if user:
                print('message received:  %s' % message)
                # Reverse Message and send it back
                print('sending back message: %s' % message[::-1])
                self.write_message(message[::-1])
        except Exception:
            pass
 
    def on_close(self):
        print('connection closed')
        if self in WSHandler.connections:
            WSHandler.connections.remove(self)

    def check_origin(self, origin):
        return True