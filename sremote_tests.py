#!/usr/bin/env python
import unittest
import subprocess
import requests
import time
class SRemoteTest(unittest.TestCase):
    def setUp(self):
    	# pass
        self.proc = subprocess.Popen(['sudo', '/home/vagrant/.virtualenvs/sremote/bin/python',
            'sremote.py', 'runserver', '--config=etc/sremote.conf'])
        print('Starting up server...')
        time.sleep(3)
        print('Server running.')

    def tearDown(self):
        self.proc.terminate()

    def test_token(self):
    	url = 'http://0.0.0.0:8080/token/'
    	headers = {'username': 'info1@example.com', 'password': 'asdf'}
    	response = requests.post(url, headers=headers)
    	print('response: %s' % response.json())

if __name__ == '__main__':
    unittest.main()