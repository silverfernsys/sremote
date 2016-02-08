#! /usr/bin/env python

import daemon
import time
import argparse
import logging
import os
from db import Db
import sys
from getpass import getpass
import ConfigParser
from setproctitle import setproctitle
from server import Server
from datetime import datetime

class Application():
    # This function combines the configuration data found in config with that
    # found in args. Those found in args overwrite those found in config.
    def _resolveConfig(self, args, config):
        tick = config.getint('sremote', 'tick')
        send_update_tick = config.getint('sremote', 'send_update_tick')
        port_number = config.getint('sremote', 'port_number')
        max_wait_seconds_before_shutdown = config.getint('sremote', 'max_wait_seconds_before_shutdown')
        try:
            daemonize = args.d
        except:
            daemonize = config.getboolean('sremote', 'daemonize')
        try:
            log_level = args.loglevel.upper()
        except:
            log_level = config.get('sremote', 'log_level')
        try:
            log_file = args.logfile
            if log_file is None:
                log_file = os.path.expanduser(config.get('sremote', 'log_file'))
        except:
            log_file = os.path.expanduser(config.get('sremote', 'log_file'))
        try:
            log_level_num = getattr(logging, log_level)
        except:
            log_level_num = logging.DEBUG
        database_dir = os.path.expanduser(config.get('sremote', 'database_dir'))
        
        return (tick, send_update_tick, port_number, max_wait_seconds_before_shutdown,
            daemonize, log_file, log_level, log_level_num, log_file, database_dir)

    def _findConfig(self):
        file_name = 'sremote.conf'
        root_path = os.path.split(sys.path[0])[0]
        file_path = os.path.join(sys.path[0], file_name)
        try:
            with open(file_path) as o:
                o.close()
                return os.path.join(root_path, file_name)
        except IOError as e:
            try:
                file_path = os.path.join(root_path, 'etc', file_name)
                with open(file_path) as o:
                    o.close()
                    return os.path.join(root_path, 'etc', file_name)
            except IOError as e:
                try:
                    file_path = os.path.join('etc', 'sremote', file_name)
                    with open(file_path) as o:
                        o.close()
                        return os.path.join('etc', 'sremote', file_name)
                except IOError as e:
                    sys.exit('Cannnot find configuration file. Tried %s/%s, %s/etc/%s, and /etc/%s\n' % (sys.path[0], file_name, sys.path[0], file_name, file_name))

    def _start(self, args):
        try:
            # print('args.config: %s' % args.config)
            self.config_path = args.config or self._findConfig()
            print('config_path: %s' % self.config_path)
            config = ConfigParser.ConfigParser()
            config.read(self.config_path)
            (self.tick, self.send_update_tick, self.port_number,
                self.max_wait_seconds_before_shutdown,
                self.daemonize, self.log_file, self.log_level,
                self.log_level_num, self.log_file, self.database_dir) = self._resolveConfig(args, config)
            # Create databases here!
            Db.instance(os.path.join(self.database_dir, 'db.sqlite'))
        except Exception as e:
            sys.exit('Cannot read configuration file. Details: %s' % e)

    def createUser(self, args):
        self._start(args)

        while True:
            username = raw_input('Enter email address: ')
            if Db.instance().user_exists(username):
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

        Db.instance().insert_user(username, password_1, admin)
        print('Successfully created user %s' % username)

    def deleteUser(self, args):
        self._start(args)

        print('Delete user: please authenticate...')
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass('Enter admin password: ')
            if not Db.instance().is_admin(admin_username):
                print('Please sign in using administrator credentials.')
            elif not Db.instance().authenticate_user(admin_username, admin_password):
                print("Username/password don't match.")
            else:
                break

        username_to_delete = raw_input('Enter username to delete: ')

        if Db.instance().user_exists(username_to_delete):
            Db.instance().delete_user(username_to_delete)
            print('Deleted user %s.' % username_to_delete)
        else:
            sys.exit("User doesn't exist. Doing nothing.")

    def listUsers(self, args):
        self._start(args)
        it = Db.instance().list_users()
        print("%s%sCreated" % ("Username".ljust(70), "Admin".ljust(20)))
        # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
        for row in it:
            if row['admin'] == 0:
                admin_str = 'N'
            else:
                admin_str = 'Y'
            print("%s%s%s" % (row['username'].ljust(70), admin_str.ljust(20), datetime.fromtimestamp(row['created']).strftime('%d-%m-%Y %H:%M:%S')))

    def listTokens(self, args):
        self._start(args)
        print("%s%sCreated" % ("Username".ljust(40), "Token".ljust(42)))
        for row in Db.instance().list_tokens():
            print("%s%s%s" % (row['username'].ljust(40), row['token'].ljust(42),
                datetime.fromtimestamp(row['created']).strftime('%d-%m-%Y %H:%M:%S')))

    def createToken(self, args):
        self._start(args)
        print('Create token: please authenticate...')
        
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass('Enter admin password: ')
            if not Db.instance().is_admin(admin_username):
                print('Please sign in using administrator credentials.')
            elif not Db.instance().authenticate_user(admin_username, admin_password):
                print("Username/password don't match.")
            else:
                break

        username = raw_input('Enter username to create a token for: ')

        if Db.instance().create_token(username):
            print('Created token belonging for %s.' % username)
        else:
            sys.exit('A token already exists for %s. Doing nothing.' % username)

    def deleteToken(self, args):
        self._start(args)
        print('Delete token: please authenticate...')
        
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass('Enter admin password: ')
            if not Db.instance().is_admin(admin_username):
                print('Please sign in using administrator credentials.')
            elif not Db.instance().authenticate_user(admin_username, admin_password):
                print("Username/password don't match.")
            else:
                break

        username = raw_input('Enter username for token to delete: ')

        if Db.instance().delete_token(username):
            print('Deleted token belonging to %s.' % username)
        else:
            sys.exit('%s has no tokens to delete.' % username)

    def runServer(self, args):
        self._start(args)
        logging.basicConfig(filename=self.log_file, format='%(asctime)s::%(levelname)s::%(name)s::%(message)s', level=self.log_level_num)
        logger = logging.getLogger('SupervisorRemote')
        logger.info('Loading configuration from %s' % self.config_path)

        if self.daemonize:
            logger.info("Daemonizing SRemote.")
            with daemon.DaemonContext():
                server = Server(port=self.port_number,
                    max_wait_seconds_before_shutdown=self.max_wait_seconds_before_shutdown,
                    tick=self.tick,
                    send_update_tick=self.send_update_tick)
        else:
            logger.info("Running SRemote.")
            server = Server(port=self.port_number,
                    max_wait_seconds_before_shutdown=self.max_wait_seconds_before_shutdown,
                    tick=self.tick,
                    send_update_tick=self.send_update_tick)

def main():
    print("app.py main()")

if __name__ == "__main__":
    main()
