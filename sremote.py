#! /usr/bin/env python

import daemon
import time
import argparse
import logging
import os
import db
import sys
from getpass import getpass
import ConfigParser
from setproctitle import setproctitle
from server import Server
from datetime import datetime

def open_file(file_name):
  file_path = os.path.join(sys.path[0], file_name)
  try:
      with open(file_path) as o:
          return (o, sys.path[0])
  except IOError as e:
      try:
          file_path = os.path.join(sys.path[0], 'etc', file_name)
          with open(file_path) as o:
              return (o, os.path.join(sys.path[0], 'etc'))
      except IOError as e:
          try:
              file_path = os.path.join('etc', 'sremote', file_name)
              with open(file_path) as o:
                  return (o, os.path.join('etc', 'sremote'))
          except IOError as e:
              error_msg = 'Cannnot find file. Tried %s/%s, %s/etc/%s, and /etc/%s\n' % (sys.path[0], file_name, sys.path[0], file_name, file_name)
              raise IOError(error_msg)

def make_config():
    filename = 'sremote.conf'
    o, path = open_file(filename)
    o.close()
    # now that we've correctly located sremote.conf successfully, load the sqlite file from the same directory
    return os.path.join(path, filename)

def createuser(args):
    try:
        config_dir = args.config or make_config()
        config = ConfigParser.ConfigParser()
        config.read(config_dir)
        database_dir = os.path.expanduser(config.get('sremote', 'database_dir'))

        try:
            # This will either create a new database if it doesn't exist or read from an existing db if it does exist.
            conn = db.connect(os.path.join(database_dir, 'db.sqlite'))
            cur = conn.cursor()
            db.create_tables(conn, cur)

            while True:
                username = raw_input('Enter email address: ')
                if db.user_exists(conn, cur, username):
                    print('Username already exists. Please pick another username.')
                else:
                    break
            while True:
                is_admin = raw_input('Admininstrative user? (y/N): ')
                if (len(is_admin) == 0) or (is_admin.upper() == 'N'):
                    admin = 0
                    break
                elif is_admin.upper() == 'Y':
                    admin = 1
                    break
            while True:
                password_1 = getpass('Enter password: ')
                password_2 = getpass('Re-enter password: ')
                if password_1 != password_2:
                    print('Passwords do not match.')
                else:
                    break

            db.insert_user(conn, cur, username, password_1, admin)
            print('Successfully created user %s' % username)
        except Exception as e:
            print("Exception connecting to sqlite database: %s " % e)
    except IOError as e:
        sys.stderr.write(e.message)
        sys.exit('Could not load configuration file. Exiting.')
    sys.exit(0)

def deleteuser(args):
    try:
        config_dir = args.config or make_config()
        config = ConfigParser.ConfigParser()
        config.read(config_dir)
        database_dir = os.path.expanduser(config.get('sremote', 'database_dir'))
        try:
            # This will either create a new database if it doesn't exist or read from an existing db if it does exist.
            conn = db.connect(os.path.join(database_dir, 'db.sqlite'))
            cur = conn.cursor()
            db.create_tables(conn, cur)

            print('Delete user: please authenticate...')
            
            while True:
                admin_username = raw_input('Enter admin username: ')
                admin_password = getpass('Enter admin password: ')
                row = db.get_user(conn, cur, admin_username)
                if row[3] != 1:
                    print('Please sign in using administrator credentials.')
                elif admin_password != row[2]:
                    print("Username/password don't match.")
                else:
                    break

            username_to_delete = raw_input('Enter username to delete: ')

            if db.user_exists(conn, cur, username_to_delete):
                db.delete_user(conn, cur, username_to_delete)
                print('Deleted user %s.' % username_to_delete)
            else:
                sys.exit("User doesn't exist.")
        except Exception as e:
            print("Exception connecting to sqlite database: %s " % e)
    except IOError as e:
        sys.stderr.write(e.message)
        sys.exit('Could not load configuration file. Exiting.')
    sys.exit(0)

def listusers(args):
    try:
        config_dir = args.config or make_config()
        config = ConfigParser.ConfigParser()
        config.read(config_dir)
        database_dir = os.path.expanduser(config.get('sremote', 'database_dir'))
        try:
            # This will either create a new database if it doesn't exist or read from an existing db if it does exist.
            conn = db.connect(os.path.join(database_dir, 'db.sqlite'))
            cur = conn.cursor()
            db.create_tables(conn, cur)
            it = db.list_users(conn, cur)
            print("%s%sCreated" % ("Username".ljust(70), "Admin".ljust(20)))
            # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            for row in it:
                if row[3] == 0:
                    admin_str = 'N'
                else:
                    admin_str = 'Y'
                print("%s%s%s" % (row[1].ljust(70), admin_str.ljust(20), datetime.fromtimestamp(row[4]).strftime('%d-%m-%Y %H:%M:%S')))
        except Exception as e:
            print("Exception connecting to sqlite database: %s " % e)
    except IOError as e:
        sys.stderr.write(e.message)
        sys.exit('Could not load configuration file. Exiting.')
    sys.exit(0)

def runserver(args):
    try:
        print(args.config)
        config_dir = args.config or make_config()
        # https://docs.python.org/2/library/configparser.html
        config = ConfigParser.ConfigParser()
        config.read(config_dir)
        tick = config.getint('sremote', 'tick')
        send_update_tick = config.getint('sremote', 'send_update_tick')
        port_number = config.getint('sremote', 'port_number')
        daemonize = config.getboolean('sremote', 'daemonize')
        log_level = config.get('sremote', 'log_level')
        log_path = os.path.expanduser(config.get('sremote', 'log_file'))
        database_dir = os.path.expanduser(config.get('sremote', 'database_dir'))

        print('tick: %s' % tick)
        print('send_update_tick: %s' % send_update_tick)
        print('port_number: %s' % port_number)
        print('daemonize: %s' % daemonize)
        print('log_level: %s' % log_level)
        print('log_path: %s' % log_path)
        print('database_dir: %s' % database_dir)

        # Parse log level
        if args.log:
            try:
                level = getattr(logging, args.log.upper())
            except:
                level = getattr(logging, log_level)
        else:
            try:
                level = getattr(logging, log_level)
            except:
                level = logging.DEBUG

        filename = args.logfile or log_path
        logging.basicConfig(filename=filename, format='%(asctime)s::%(levelname)s::%(name)s::%(message)s', level=level)
        logger = logging.getLogger('SupervisorRemote')
        logger.info('Loading configuration from %s' % config_dir)

        daemonize = args.d or daemonize

        if daemonize:
            logger.info("Daemonizing SRemote.")
            with daemon.DaemonContext():
                server = Server(config)
        else:
            logger.info("Running SRemote.")
            server = Server(config)
    except IOError as e:
        sys.stderr.write(e.message)
        sys.exit('Could not load configuration file. Exiting: %s' % e)

def main():
    setproctitle("SupervisorRemote")
    # https://docs.python.org/2/library/argparse.html
    parser = argparse.ArgumentParser(prog='sremote.py')
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_createuser = subparsers.add_parser('createuser', help='create a new user')
    parser_createuser.add_argument("--config", help="path to the configuration file.")
    parser_createuser.set_defaults(func=createuser)
    parser_deleteuser = subparsers.add_parser('deleteuser', help='delete an existing user')
    parser_deleteuser.add_argument("--config", help="path to the configuration file.")
    parser_deleteuser.set_defaults(func=deleteuser)
    parser_listusers = subparsers.add_parser('listusers', help='list existing users')
    parser_listusers.add_argument("--config", help="path to the configuration file.")
    parser_listusers.set_defaults(func=listusers)
    parser_runserver = subparsers.add_parser('runserver', help='run the SupervisorRemote server')
    parser_runserver.set_defaults(func=runserver)
    parser_runserver.add_argument("--config", help="path to the configuration file.")
    parser_runserver.add_argument("--port", type=int, help="the port to use. default is 8888.")
    parser_runserver.add_argument("-d", action="store_true", help="daemonize application.")
    parser_runserver.add_argument("--log", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="log level.")
    parser_runserver.add_argument("--logfile", help="path to the log file.")

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
