import unittest
import json

from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestCaseNew(BaseTest):

    def setUp(self):
        super(SmartLockTestCaseNew, self).setUp()
        self.app.post('/register-user', data=dict(email="test@mail.com", password="python"))

    def tearDown(self):
        super(SmartLockTestCaseNew, self).tearDown()

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
        response = self.app.post('/user', data=dict(email="test2@mail.com", password="python"))
        self.assertEqual(201, response.status_code)
        self.assertEqual(json.loads(response.data)['email'], "test2@mail.com")
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_register_fail(self):
        """Fail to provide Registration info - no password"""
        response = self.app.post('/user', data=dict(email="test2@mail.com"))
        self.assertEqual(400, response.status_code)

    def test_already_registered(self):
        """Fail due to email already being in db"""
        response = self.app.post('/user', data=dict(email="test@mail.com", password="python"))
        self.assertEqual(406, response.status_code)
        self.assertEqual(json.loads(response.data)['email'], "test@mail.com")


if __name__ == '__main__':
    unittest.main()
