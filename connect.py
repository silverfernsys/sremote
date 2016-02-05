#! /usr/bin/env python
# http://stackoverflow.com/questions/11729159/use-python-xmlrpclib-with-unix-domain-sockets

import httplib
import socket
import xmlrpclib


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


def server():
    return xmlrpclib.Server('http://arg_unused', transport=UnixStreamTransport('/var/run/supervisor.sock'))


def main():
    server = xmlrpclib.Server('http://arg_unused', transport=UnixStreamTransport('/var/run/supervisor.sock'))
    print(server.supervisor.getState())
    print(server.system.listMethods())
    print(server.supervisor.getAllProcessInfo())


if __name__ == '__main__':
    main()
