#!/usr/bin/env python
import httplib
import json
import logging
import os
import socket
import time
import threading
import xmlrpclib
from ws import WSHandler
from procinfo import ProcInfo

class UnixStreamHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.host)


class UnixStreamTransport(xmlrpclib.Transport, object):
    def __init__(self, socket_path):
        self.socket_path = socket_path
        super(UnixStreamTransport, self).__init__()

    def make_connection(self, host):
        return UnixStreamHTTPConnection(self.socket_path)


class ProcessUpdater():
    """
    This class pushes and pulls process update information.
    """
    version = 0.0

    def __init__(self, **kwargs):
        self.update_interval = kwargs['tick']
        self.push_interval = kwargs['send_update_tick']
        self.xmlrpc = xmlrpclib.Server('http://arg_unused',
            transport=UnixStreamTransport('/var/run/supervisor.sock'))
        ProcessUpdater.version = float(self.xmlrpc.supervisor.getVersion())

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
