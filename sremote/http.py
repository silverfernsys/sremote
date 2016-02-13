#!/usr/bin/env python
import json
from socket import gethostname
import tornado.httpserver
from procinfo import ProcInfo
from processupdater import ProcessUpdater
from models.user import User
from models.token import Token

class HTTPVersionHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self):
        data = {'version': ProcessUpdater.version,
        'hostname': gethostname()}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))


class HTTPStatusHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self):
        try:
            auth_token = self.request.headers.get('authorization')
            token = Token.tokens().get(token=auth_token)
            if token and token.user:
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
                data = {'processes': processes, 'version': ProcessUpdater.version}
            else:
                data = {'error': 'not authorized'}
        except Exception as e:
            print('Error: %s' % e)
            try:
                logger = logging.getLogger('Web Server')
                logger.error(e)
            except:
                pass
            data = {'error': e}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

class HTTPTokenHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def get(self):
        try:
            username = self.request.headers.get('username')
            password = self.request.headers.get('password')
            user = User.users().get(username=username)
            if user.authenticate(password):
                token = Token.tokens().get_token_for_user(user)
                if not token:
                    token = Token(user=user)
                    token.save()
                data = {'token': token.token}
            else:
                data = {'error': 'invalid username/password'}
        except Exception as e:
            data = {'error': str(e)}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))
