import SmartLockServer
import unittest
import models
from tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestCase(BaseTest):

    def setUp(self):
        super(SmartLockTestCase, self).setUp()
        self.app.post('/register', data=dict(email="test@mail.com", password="python"))
        SmartLockServer.db.session.commit()

    def tearDown(self):
        super(SmartLockTestCase, self).tearDown()

    def test_auth_bad(self):
        """ Ensure that bad user credentials are rejected - Sam """
        response = self.app.get('/protected-resource')
        self.assertEqual(401, response.status_code)

    def test_auth_good(self):
        """ Ensure that good user credentials are accepted - Sam """
        response = self.app.get('/protected-resource', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_register_success(self):
        """Register to gain access to protected resource"""
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(401, response.status_code)
        response = self.app.post('/register', data=dict(email="test2@mail.com", password="python"))
        self.assertEqual(201, response.status_code)
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(200, response.status_code)



if __name__ == '__main__':
    unittest.main()
