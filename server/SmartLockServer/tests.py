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
        response = self.app.get('/protected-resource', headers=self.auth_header("mingles", "python"))
        self.assertEqual(200, response.status_code)

    def test_open_lock_good(self):
        """Ensure that good user credentials are accepted with the open lock """
        response = self.app.put('/open/123', headers=self.auth_header("mingles", "python"))
        self.assertEqual(200, response.status_code)

    def test_open_lock_bad_id(self):
        """Ensure that good user credentials fail with the an unassociated lock"""
        response = self.app.get('/open/124', headers=self.auth_header("mingles", "python"))
        self.assertEqual(405, response.status_code)

    def test_open_lock_nae_lock(self):
        """Ensure that good user credentials are not accepted without a lock"""
        response = self.app.get('/open', headers=self.auth_header("mingles", "python"))
        self.assertEqual(404, response.status_code)

    def test_open_lock_wrong_login(self):
        """Ensure that bad password, but corect username is rejected with correct lock"""
        response = self.app.get('/open/123', headers=self.auth_header("mingles", "iscool123"))
        self.assertEqual(405, response.status_code)


if __name__ == '__main__':
    unittest.main()
