#! /usr/bin/env python

import argparse
from setproctitle import setproctitle
from app import Application

def main():
    setproctitle("SupervisorRemote")
    app = Application()
    # https://docs.python.org/2/library/argparse.html
    parser = argparse.ArgumentParser(prog='sremote.py')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_createuser = subparsers.add_parser('createuser', help='create a new user')
    parser_createuser.add_argument("--config", help="path to the configuration file.")
    parser_createuser.set_defaults(func=app.createUser)
    parser_deleteuser = subparsers.add_parser('deleteuser', help='delete an existing user')
    parser_deleteuser.add_argument("--config", help="path to the configuration file.")
    parser_deleteuser.set_defaults(func=app.deleteUser)
    parser_listusers = subparsers.add_parser('listusers', help='list existing users')
    parser_listusers.add_argument("--config", help="path to the configuration file.")
    parser_listusers.set_defaults(func=app.listUsers)
    parser_listtokens = subparsers.add_parser('listtokens', help='list authentication tokens')
    parser_listtokens.add_argument("--config", help="path to the configuration file.")
    parser_listtokens.set_defaults(func=app.listTokens)
    parser_createtoken = subparsers.add_parser('createtoken', help="create a token")
    parser_createtoken.add_argument("--config", help="path to the configuration file.")
    parser_createtoken.set_defaults(func=app.createToken)
    parser_deletetoken = subparsers.add_parser('deletetoken', help="delete a user's token")
    parser_deletetoken.add_argument("--config", help="path to the configuration file.")
    parser_deletetoken.set_defaults(func=app.deleteToken)
    parser_runserver = subparsers.add_parser('runserver', help='run the SupervisorRemote server')
    parser_runserver.set_defaults(func=app.runServer)
    parser_runserver.add_argument("--config", help="path to the configuration file.")
    parser_runserver.add_argument("--port", type=int, help="the port to use. default is 8888.")
    parser_runserver.add_argument("-d", action="store_true", help="daemonize application.")
    parser_runserver.add_argument("--loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="log level.")
    parser_runserver.add_argument("--logfile", help="path to the log file.")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
