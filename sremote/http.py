#!/usr/bin/env python
import json
import tornado.httpserver
from models.db import Db

class HTTPHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(HTTPHandler, self).__init__(application, request, **kwargs)
        print("HTTPHandler.__init__")

    def __del__(self):
        print("HTTPHandler.__del__")

    def get(self):
        data = {'key': 'value'}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))


class HTTPStatusHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self):
        try:
            token = self.request.headers.get('authorization')
            user = Db.instance().get_user_with_token(token)
            if user is None:
                data = {'error': 'not authorized'}
            else:
                timestamp_str = self.get_query_argument('timestamp', None, True)
                if timestamp_str != None:
                    timestamp = float(timestamp_str)
                else:
                    timestamp = -1.0
                processes = []
                for p in ProcInfo.all():
                    processes.append({'group': p.group, 'name': p.name, 'pid':p.pid, 'state': p.state,
                        'statename': p.statename, 'start': p.start, 'cpu': p.get_cpu(timestamp),
                        'mem': p.get_mem(timestamp)})
                data = {'processes': processes, 'version': SendUpdates.version}
        except Exception as e:
            print('Error: %s' % e)
            logger = logging.getLogger('Web Server')
            logger.error(e)
            data = {'error': e}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

class HTTPTokenHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def post(self):
        username = self.request.headers.get('username')
        password = self.request.headers.get('password')
        if Db.instance().authenticate_user(username, password):
            Db.instance().create_token(username)
            token = Db.instance().get_token(username)
            data = {'token': token}
        else:
            data = {'error': 'invalid username/password'}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))
