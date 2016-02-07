#!/usr/bin/env python
import sys
import socket
import logging
import json


class EventListener():
    def __init__(self):
        self.logger = logging.getLogger('Event Listener')
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def write_stdout(self, s):
        # only eventlistener protocol messages may be sent to stdout
        sys.stdout.write(s)
        sys.stdout.flush()

    def write_stderr(self, s):
        sys.stderr.write(s)
        sys.stderr.flush()

    def start(self):
        # Connect the socket to the port where the server is listening
        server_address = "/run/sremote.sock"
        self.logger.info('Attemping to connect to %s' % server_address)
        try:
            self.socket.connect(server_address)
        except socket.error as error:
            self.logger.error(error)
            sys.exit(1)

        while 1:
            # transition from ACKNOWLEDGED to READY
            self.write_stdout('READY\n')
            
            # read header line
            line = sys.stdin.readline()

            # read event payload and send to socket
            # don't forget the new-line character!!!!
            headers = dict([ x.split(':') for x in line.split() ])
            raw_data = sys.stdin.read(int(headers['len']))
            data = dict([ x.split(':') for x in raw_data.split()])

            self.logger.info(raw_data)

            try:
                response = {}
                response['name'] = data['processname']
                response['group'] = data['groupname']
                response['from_state'] = data['from_state']
                response['eventname'] = headers['eventname']
                response['statename'] = headers['eventname'].split('_')[2]
                try:
                    response['pid'] = data['pid']
                except:
                    response['pid'] = None

                json_str = json.dumps(response)
                self.socket.sendall('LENGTH:%s\n' % len(json_str))
                self.socket.sendall(json_str)
                self.logger.info(json_str)
            except Exception as e:
                self.logger.error(e)

            # transition from READY to ACKNOWLEDGED
            self.write_stdout('RESULT 2\nOK')

def main():
    logging.basicConfig(filename='/tmp/eventlistener.log', format='%(asctime)s::%(levelname)s::%(name)s::%(message)s', level=logging.DEBUG)
    event_listener = EventListener()
    event_listener.start()


if __name__ == '__main__':
    main()
