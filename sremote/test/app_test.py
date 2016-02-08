import unittest
import tempfile
import os
import argparse
import tempfile
import ConfigParser
import shutil
import mock
from sremote.app import Application

class ApplicationTest(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for writing the config file to
        # as well as for creating testing databases in.
        self.temp_dir = tempfile.mkdtemp()
        print('ApplicationTest::temp_dir: %s' % self.temp_dir)
        
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

        # Writing our configuration file to 'sremote.conf'
        with open(os.path.join(self.temp_dir, 'sremote.conf'), 'wb') as configfile:
            config.write(configfile)

        parser = argparse.ArgumentParser(prog='sremote.py')
        parser.add_argument("--config", help="path to the configuration file.")

        # Create our arguments programmatically
        self.args = parser.parse_args(['--config', os.path.join(self.temp_dir, 'sremote.conf')])
        self.app = Application()

    def tearDown(self):
        self.app = None
        shutil.rmtree(self.temp_dir)

    def testCreateUser(self):
        # @mock.patch('sys.stdin')
        # def getpass_mock():
        #     yield 'asdf'

        # with mock.patch('getpass.getpass', side_effect=['asdf', 'asdf']):
        with mock.patch('__builtin__.raw_input', side_effect=['info@example.com', 'y', 'asdf', 'asdf']):
            self.app.createUser(self.args)

