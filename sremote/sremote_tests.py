#!/usr/bin/env python
import unittest
import subprocess
import requests
import time
import json
from websocket import create_connection

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

    # def test_token(self):
    # 	url = 'http://0.0.0.0:8080/token/'
    #     # Test with correct username/password
    # 	headers = {'username': 'info3@example.com', 'password': 'asdf'}
    # 	response = requests.post(url, headers=headers)
    #     self.assertTrue('token' in json.loads(response.text), "token returned")

    #     # Test with incorrect password
    #     headers = {'username': 'info3@example.com', 'password': 'qwer'}
    #     response = requests.post(url, headers=headers)
    #     self.assertTrue('error' in json.loads(response.text), "error returned")

    #     # Test with non-existent username
    #     headers = {'username': 'info99@example.com', 'password': 'asdf'}
    #     response = requests.post(url, headers=headers)
    #     self.assertTrue('error' in json.loads(response.text), "error returned")

    # def test_status(self):
    #     # Obtain an authorization token
    #     url = 'http://0.0.0.0:8080/token/'
    #     headers = {'username': 'info3@example.com', 'password': 'asdf'}
    #     response = requests.post(url, headers=headers)
    #     json_data = json.loads(response.text)
    #     self.assertTrue('token' in json_data, "token returned")

    #     # Get status
    #     url = 'http://0.0.0.0:8080/status/'
    #     headers = {'authorization': json_data['token']}
    #     response = requests.get(url, headers=headers)
    #     json_data = json.loads(response.text)
    #     self.assertTrue('version' in json_data, "'version' in response json key")
    #     self.assertTrue('processes' in json_data, "'processes' in response json key")

    def test_ws(self):
        url = 'http://0.0.0.0:8080/token/'
        headers = {'username': 'info@example.com', 'password': 'asdf'}
        response = requests.post(url, headers=headers)
        json_data = json.loads(response.text)
        self.assertTrue('token' in json_data, "token returned")

        ws = create_connection("ws://127.0.0.1:8080/ws/", header=["authorization: %s" % json_data['token']])
        ws.send("Hello, World")
        print("Sent")
        print("Receiving...")
        result = ws.recv()
        print("Received '%s'" % result)
        # ws.close()
        # ws.send(json.dumps({}))
        print(dir(ws))

        ws_1 = create_connection("ws://127.0.0.1:8080/ws/", header=["authorization: garbage"])
        ws_1.send("Hi there unauthorized user!")
        print("Sent")
        print("Receiving...")
        result = ws_1.recv()
        print("Received '%s'" % result)
        # ws_1.close()

if __name__ == '__main__':
    unittest.main()