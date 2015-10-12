import os
import SmartLockServer
import unittest
import tempfile
import json
from base64 import b64encode

__author__ = 'mingles'


class SmartLockTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, SmartLockServer.app.config['DATABASE'] = tempfile.mkstemp()
        SmartLockServer.app.config['TESTING'] = True
        self.app = SmartLockServer.app.test_client()
        # SmartLockServer.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(SmartLockServer.app.config['DATABASE'])

    def auth_header(self, username, password):
        """
        :param username: the user to log in's username
        :param password: the user to log in's password
        :return: the authentication header as a string string
        """
        return {
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password))
        }

    def test_hello_world(self):
        """ Ensure that Hello World end Point works """
        response = self.app.get('/')
        self.assertEqual({'hello': 'world'}, json.loads(response.data))

    def test_auth_bad(self):
        """ Ensure that bad user credentials are rejected - Sam """
        response = self.app.get('/protected-resource')
        self.assertEqual(403, response.status_code)

    def test_auth_good(self):
        """ Ensure that good user credentials are accepted - Sam """
        response = self.app.get('/protected-resource', headers=self.auth_header("miguel", "python"))
        self.assertEqual(200, response.status_code)


if __name__ == '__main__':
    unittest.main()
