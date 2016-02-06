#!/usr/bin/env python
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import settings
import time
import threading
import logging
import signal
import json
import os
from connect import server
# from eventserver import EventServer
from procinfo import ProcInfo
from helpers import binary_search


# The SendUpdates class sends updates of CPU and Memory usage of supervisor processes.
class SendUpdates():
    version = 0.0

    def __init__(self, config):
        print("SendUpdates.__init__")
        self.update_interval = config.getint('sremote', 'tick')
        self.push_interval = config.getint('sremote', 'send_update_tick')
        self.xmlrpc = server()
        SendUpdates.version = float(self.xmlrpc.supervisor.getVersion())

        data = self.xmlrpc.supervisor.getAllProcessInfo()

        # print(self.xmlrpc.supervisor.getState())
        # print(self.xmlrpc.system.listMethods())
        # print('data: %s' % data)
        for d in data:
            ProcInfo(d['group'], d['name'], d['pid'], d['state'], d['statename'], d['start'])

        update_stats_thread = threading.Thread(target=self.update_stats, args=())
        update_stats_thread.daemon = True
        update_stats_thread.start()

        push_data_thread = threading.Thread(target=self.push_data, args=())
        push_data_thread.daemon = True
        push_data_thread.start()

        event_server_thread = threading.Thread(target=self.event_server, args=())
        event_server_thread.daemon = True
        event_server_thread.start()

    def update_stats(self):
        while True:
            ProcInfo.updateall()
            time.sleep(self.update_interval)

    def push_data(self):
        while True:
            if (len(WSHandler.connections) > 0):
                data = []
                for info in ProcInfo.all():
                    data.append(info.to_dict())
                json_str = json.dumps(data)
                print(json_str)
                for conn in WSHandler.connections:
                    try:
                        conn.write_message(json_str)
                    except Exception as e:
                        print("Exception writing to websocket: %s" % e)
            else:
                # print("No websocket connections.")
                pass

            time.sleep(self.push_interval)

    def event_server(self):
        logger = logging.getLogger('Event Server')
        # Create a UDS socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        server_address = '/run/sremote.sock'

        # Make sure the socket does not already exist
        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise

        logger.info('Starting server at %s' % server_address)
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            logger.info('Waiting for a connection...')
            connection, client_address = sock.accept()
            logger.info('Connected to client.')
            try:
                handle = connection.makefile()
                while True:
                    line = handle.readline()
                    headers = dict([ x.split(':') for x in line.split() ])
                    data = handle.read(int(headers['LENGTH']))
                    json_data = json.loads(data)
                    p = ProcInfo.get(json_data['group'], json_data['name'])
                    p.statename = json_data['statename']
                    if (p.statename == 'STOPPED'):
                        p.pid = None
                    else:
                        p.pid = json_data['pid']

                    # We need to now send data off on the websocket!
            except Exception as e:
                print('Exception: %s' % e)
                print('Closing connection...')
                logger.info('Closing connection...')
                connection.close()
                logger.info('Connection closed.')


class WSHandler(tornado.websocket.WebSocketHandler):
    connections = []

    # def __init__(self, application, request, **kwargs):
    #     super(WSHandler, self).__init__(application, request, **kwargs)
    #     print("WSHandler")

    # def __del__(self):
    #     print("WSHandler.__del__")

    def open(self):
        print('new connection')
        if(self.request.headers['Authorization'] != settings.AUTH_KEY):
            self.close()
        else:
            WSHandler.connections.append(self)
      
    def on_message(self, message):
        try:
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
            timestamp_str = self.get_query_argument('timestamp', None, True)
            if timestamp_str != None:
                timestamp = float(timestamp_str)
            else:
                timestamp = -1.0

            print('HTTPStatusHandler.get: timestamp_str: %s' % timestamp_str)
            processes = []
            for p in ProcInfo.all():
                processes.append({'group': p.group, 'name': p.name, 'pid':p.pid, 'state': p.state,
                    'statename': p.statename, 'start': p.start, 'cpu': binary_search(p.cpu, timestamp),
                    'mem': binary_search(p.mem, timestamp)})
            data = {'processes': processes, 'version': SendUpdates.version}
        except Exception as e:
            print('Error: %s' % e)
            logger = logging.getLogger('Web Server')
            logger.error(e)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

class HTTPTokenHandler(tornado.web.RequestHandler):
    @tornado.web.addslash
    def post(self):
        print('HTTPTokenHandler')
        print('HTTPTokenHandler: %s' % self.request.headers.get('username'))
        print('HTTPTokenHandler: %s' % self.request.headers.get('password'))
        data = {'token': 'ASDFHREWLQWEKFKEQLWKEFNEKWLQKFN'}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(data))

class Server():
    # Adapted from code found at https://gist.github.com/mywaiting/4643396
    def sig_handler(self, sig, frame):
        self.logger.warning("Caught signal: %s", sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('Web Server')

        application = tornado.web.Application([
            (r'/', HTTPHandler),
            (r'/status/', HTTPStatusHandler),
            (r'/token/', HTTPTokenHandler),
            (r'/ws', WSHandler),
        ])

        send_updates = SendUpdates(config)
        # event_server = EventServer(threaded=True)
        port = self.config.getint('sremote', 'port_number')
        server = tornado.httpserver.HTTPServer(application)
        server.listen(port)
        self.logger.info('Running on port %s' % port)
        self.server = server
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        tornado.ioloop.IOLoop.instance().start()
        self.logger.info("Exit...")

    def shutdown(self):
        self.logger.info('Stopping HTTP Server.')
        self.server.stop()
        seconds = self.config.getint('sremote', 'max_wait_seconds_before_shutdown')
        self.logger.info('Will shutdown in %s seconds...', seconds)
        io_loop = tornado.ioloop.IOLoop.instance()
        deadline = time.time() + seconds

        def stop_loop():
            now = time.time()
            if now < deadline and (io_loop._callbacks or io_loop._timeouts):
                io_loop.add_timeout(now + 1, stop_loop)
            else:
                io_loop.stop()
                self.logger.info('Shutdown')
        stop_loop()
