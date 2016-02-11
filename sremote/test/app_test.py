import unittest
import tempfile
import io
import os
import argparse
import tempfile
import ConfigParser
import shutil
import mock
import sys
import threading
from time import sleep
from sremote.app import Application
from sremote.models.user import User
from sremote.models.token import Token
from sremote.models.database import DatabaseManager

class ApplicationTest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for writing the config file to
        # as well as for creating testing databases.
        self.temp_dir = tempfile.mkdtemp()

        # Create a config file programmatically.
        config = ConfigParser.RawConfigParser()
        config.add_section('sremote')
        config.set('sremote', 'tick', '3')
        config.set('sremote', 'send_update_tick', '5')
        config.set('sremote', 'max_wait_seconds_before_shutdown', '3')
        config.set('sremote', 'port_number', '8080')
        config.set('sremote', 'daemonize', 'False')
        config.set('sremote', 'log_level', 'DEBUG')
        config.set('sremote', 'log_file', os.path.join(self.temp_dir, 'sremote.log'))
        config.set('sremote', 'database_dir', self.temp_dir)

        # Writing our configuration file to 'temp_dir/sremote.conf'
        with open(os.path.join(self.temp_dir, 'sremote.conf'), 'wb') as configfile:
            config.write(configfile)

        parser = argparse.ArgumentParser(prog='sremote.py')
        parser.add_argument("--config", help="path to the configuration file.")

        # Create arguments programmatically
        self.args = parser.parse_args(['--config', os.path.join(self.temp_dir, 'sremote.conf')])
        self.app = Application()

        # Overwrite default database with one in memory.
        # from sremote.models.database import DatabaseManager
        DatabaseManager.add('default', os.path.join(self.temp_dir, 'db.sqlite'))

    def tearDown(self):
        self.app = None
        shutil.rmtree(self.temp_dir)

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_create_user(self, getuser, getpassword):
        getuser.side_effect = ('jim@example.com', 'y',)
        getpassword.side_effect = ('asdfasdf', 'asdfasdf',)

        User._users = None
        Token._tokens = None

        # Redirect sys.stdout to temp_stdout so that we can read
        # the terminal output from 'createUser' and ensure that
        # it matches our expectations. --Mr. Verbosity
        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.createUser(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)
        output_line = temp_stdout.readline()
        self.assertEqual(output_line, 'Successfully created user jim@example.com\n')

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_delete_user(self, getuser, getpassword):
        getuser.side_effect = ('jane@example.com', 'jack@example.com',)
        getpassword.side_effect = ('asdfasdf',)

        User._users = None
        Token._tokens = None

        user_0 = User('jane@example.com', 'asdfasdf', True)
        user_0.save()
        user_1 = User('jill@example.com', 'qwerqwer', False)
        user_1.save()
        user_3 = User('jack@example.com', 'zxcvzxcv', False)
        user_3.save()
        user_4 = User('marc@example.com', 'wertwert', True)
        user_4.save()

        # deleteUser will create a new database connection, so best to null out the current
        # one first! This will force User.user() to access the new default database.
        # I hate this hack!!!!
        User._users = None
        Token._tokens = None
        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.deleteUser(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)

        self.assertEqual(temp_stdout.readline(), 'Delete user: please authenticate...\n')
        self.assertEqual(temp_stdout.readline(), 'Deleted user jack@example.com.\n')

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_list_users(self, getuser, getpassword):
        User._users = None
        Token._tokens = None

        user_0 = User('jane@example.com', 'asdfasdf', True)
        user_0.save()
        user_1 = User('jill@example.com', 'qwerqwer', False)
        user_1.save()
        user_3 = User('jack@example.com', 'zxcvzxcv', False)
        user_3.save()
        user_4 = User('marc@example.com', 'wertwert', True)
        user_4.save()

        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.listUsers(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)
        self.assertTrue('Username' in temp_stdout.readline())
        self.assertTrue('jane@example.com' in temp_stdout.readline())

    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_create_token(self, getuser, getpassword):
        User._users = None
        Token._tokens = None
        
        getuser.side_effect = ('jane@example.com', 'jill@example.com',)
        getpassword.side_effect = ('asdfasdf',)

        user_0 = User('jane@example.com', 'asdfasdf', True)
        user_0.save()
        user_1 = User('jill@example.com', 'qwerqwer', False)
        user_1.save()

        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.createToken(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)
        self.assertTrue('Create token: please authenticate...' in temp_stdout.readline())
        self.assertTrue('created for jill@example.com' in temp_stdout.readline())


    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_delete_token(self, getuser, getpassword):
        User._users = None
        Token._tokens = None
        
        getuser.side_effect = ('jane@example.com', 'jill@example.com',)
        getpassword.side_effect = ('asdfasdf',)

        user_0 = User('jane@example.com', 'asdfasdf', True)
        user_0.save()
        user_1 = User('jill@example.com', 'qwerqwer', False)
        user_1.save()

        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.deleteToken(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)
        self.assertTrue('Delete token: please authenticate...' in temp_stdout.readline())
        self.assertTrue('jill@example.com has no tokens to delete.' in temp_stdout.readline())


    @mock.patch('getpass.getpass')
    @mock.patch('__builtin__.raw_input')
    def test_list_tokens(self, getuser, getpassword):
        User._users = None
        Token._tokens = None

        temp_stdout = io.BytesIO()
        sys.stdout = temp_stdout
        self.app.listTokens(self.args)
        sys.stdout = sys.__stdout__
        temp_stdout.seek(0)
        self.assertEqual(len(temp_stdout.readlines()), 1)
