#!/usr/bin/env python
import unittest
import subprocess
import requests
import time
import json

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
        # Test with correct username/password
    	headers = {'username': 'info3@example.com', 'password': 'asdf'}
    	response = requests.post(url, headers=headers)
        self.assertTrue('token' in json.loads(response.text), "token returned")

        # Test with incorrect password
        headers = {'username': 'info3@example.com', 'password': 'qwer'}
        response = requests.post(url, headers=headers)
        self.assertTrue('error' in json.loads(response.text), "error returned")

        # Test with non-existent username
        headers = {'username': 'info31@example.com', 'password': 'asdf'}
        response = requests.post(url, headers=headers)
        self.assertTrue('error' in json.loads(response.text), "error returned")


if __name__ == '__main__':
    unittest.main()