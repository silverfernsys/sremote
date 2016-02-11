#! /usr/bin/env python

import daemon
import time
import argparse
import logging
import os
from models.db import Db
from models.database import DatabaseManager
import sys
import getpass
# from getpass import getpass
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
            # print('config_path: %s' % self.config_path)
            config = ConfigParser.ConfigParser()
            config.read(self.config_path)
            (self.tick, self.send_update_tick, self.port_number,
                self.max_wait_seconds_before_shutdown,
                self.daemonize, self.log_file, self.log_level,
                self.log_level_num, self.log_file, self.database_dir) = self._resolveConfig(args, config)
            # Create databases here!
            # Db.instance(os.path.join(self.database_dir, 'db.sqlite'))
            DatabaseManager.add('default', os.path.join(self.database_dir, 'db.sqlite'))
        except Exception as e:
            sys.exit('Cannot read configuration file. Details: %s' % e)

    def createUser(self, args):
        self._start(args)
        from models.user import User

        while True:
            username = raw_input('Enter email address: ')
            if User.users().get(username=username):
                print('Username already exists. Please pick another username.')
            else:
                break
            print('username: %s' % username)
        while True:
            is_admin = raw_input('Admininstrative user? (y/N): ')
            if (len(is_admin) == 0) or (is_admin.upper() == 'N'):
                admin = False
                break
            elif is_admin.upper() == 'Y':
                admin = True
                break
        while True:
            password_1 = getpass.getpass('Enter password: ')
            password_2 = getpass.getpass('Re-enter password: ')
            if password_1 != password_2:
                print('Passwords do not match.')
            else:
                break

        user = User(username, password_1, admin)
        user.save()
        # Db.instance().insert_user(username, password_1, admin)
        print('Successfully created user %s' % username)

    def deleteUser(self, args):
        self._start(args)
        from models.user import User

        print('Delete user: please authenticate...')
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass.getpass('Enter admin password: ')
            user = User.users().get(username=admin_username)
            if not user.admin:
                print('Please sign in using administrator credentials.')
            elif not user.authenticate(admin_password):
                print("Username/password don't match.")
            else:
                break

        username_to_delete = raw_input('Enter username to delete: ')
        if User.users().get(username=username_to_delete).delete():
            # Db.instance().delete_user(username_to_delete)
            print('Deleted user %s.' % username_to_delete)
        else:
            sys.exit("User doesn't exist. Doing nothing.")

    def listUsers(self, args):
        self._start(args)
        from models.user import User
        print("%s%sCreated" % ("Username".ljust(70), "Admin".ljust(20)))
        for user in User.users().all():
            if user.admin:
                admin_str = 'Y'
            else:
                admin_str = 'N'
            # https://docs.python.org/2/library/datetime.html#strftime-strptime-behavior
            line = "%s%s%s" % (user.username.ljust(70), admin_str.ljust(20), datetime.fromtimestamp(user.created).strftime('%d-%m-%Y %H:%M:%S'))
            print(str(line))

    def listTokens(self, args):
        self._start(args)
        from models.token import Token
        print("%s%sCreated" % ("Username".ljust(40), "Token".ljust(42)))
        for token in Token.tokens.all():
            print("%s%s%s" % (token.user.username.ljust(40), token.token.ljust(42),
                datetime.fromtimestamp(token.created).strftime('%d-%m-%Y %H:%M:%S')))

    def createToken(self, args):
        self._start(args)
        print('Create token: please authenticate...')
        from models.user import User
        from models.token import Token
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass.getpass('Enter admin password: ')
            if not User.users.get(username=admin_username).admin:
                print('Please sign in using administrator credentials.')
            elif not User.users.get(username=admin_username).authenticate(admin_password):
                print("Username/password don't match.")
            else:
                break

        username = raw_input('Enter username to create a token for: ')
        user = User.users.get(username=username)
        if user:
            try:
                token = Token(user=user)
                token.save()
                print('Token %s created for %s' % (token.token, username))
            except:
                sys.exit('A token already exists for %s. Doing nothing.' % username)
        else:
            sys.exit('A user with username %s does not exist.' % username)

    def deleteToken(self, args):
        self._start(args)
        print('Delete token: please authenticate...')
        from models.user import User
        from models.token import Token
        while True:
            admin_username = raw_input('Enter admin username: ')
            admin_password = getpass.getpass('Enter admin password: ')
            if not User.users.get(username=admin_username).admin: #Db.instance().is_admin(admin_username):
                print('Please sign in using administrator credentials.')
            elif not User.users.get(username=admin_username).authenticate(admin_password): #Db.instance().authenticate_user(admin_username, admin_password):
                print("Username/password don't match.")
            else:
                break

        username = raw_input('Enter username for token to delete: ')
        user = User.users.get(username=username)
        if user:
            token = Token.tokens.get_token_for_user(user=user)
            if token:
                token.delete()
                print('Deleted token belonging to %s.' % username)
            else:
                sys.exit('%s has no tokens to delete.' % username)
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
