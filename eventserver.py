#!/usr/bin/env python
import socket
import sys
import os
import logging
import threading
import json

# https://pymotw.com/2/socket/uds.html
# Unix Domain Sockets
class EventServer():
    def __init__(self, threaded=False):
        if threaded:
            thread = threading.Thread(target=self.start, args=())
            thread.daemon = True
            thread.start()

    def start(self):
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
            # print >>sys.stderr, 'waiting for a connection'
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
                    print(json_data)
            except Exception as e:
                print('Exception: %s' % e)
                print('Closing connection...')
                logger.info('Closing connection...')
                connection.close()
                logger.info('Connection closed.')


def main():
    logging.basicConfig(filename='/tmp/eventserver.log', format='%(asctime)s::%(levelname)s::%(name)s::%(message)s', level=logging.DEBUG)
    event_server = EventServer()
    event_server.start()


if __name__ == '__main__':
    main()
