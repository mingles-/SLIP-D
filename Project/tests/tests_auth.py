import unittest
import json

from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestCaseAuth(BaseTest):

    def setUp(self):
        super(SmartLockTestCaseAuth, self).setUp()
        self.register_user(username="test@mail.com", password="python")

    def tearDown(self):
        super(SmartLockTestCaseAuth, self).tearDown()

    def test_auth_bad(self):
        """ Ensure that bad user credentials are rejected - Sam """
        response = self.app.get('/protected-resource')
        self.assertEqual(401, response.status_code)

    def test_auth_bad2(self):
        """ Ensure that bad user credentials are rejected - Sam """
        response = self.app.get('/protected-resource', headers=self.auth_header("", ""))
        self.assertEqual(401, response.status_code)

    def test_auth_good(self):
        """ Ensure that good user credentials are accepted - Sam """
        response = self.app.get('/protected-resource', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_register_success(self):
        """Register to gain access to protected resource"""
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(401, response.status_code)
        response = self.register_user(username="test2@mail.com", password="python")
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
        response = self.register_user(username="test@mail.com", password="python")
        self.assertEqual(406, response.status_code)
        self.assertEqual(json.loads(response.data)['email'], "test@mail.com")

    def test_user_detail(self):
        """successfully get user info"""
        response = self.register_user(username="test2@mail.com", password="python")
        user_id = json.loads(response.data)['id']
        response = self.app.get('/user/' + str(user_id), headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(json.loads(response.data)['email'], "test2@mail.com")

    def test_me(self):
        """Test me Endpoint"""
        response = self.app.get('/me', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(json.loads(response.data)['email'], "test@mail.com")

    def test_register_name(self):
        """Register a users first and second name"""
        response = self.app.post('/user', data=dict(email="test2@mail.com", password="python", first_name="mingley", last_name="dingly"))
        self.assertEqual(json.loads(response.data)["first_name"], "mingley")
        self.assertEqual(json.loads(response.data)["last_name"], "dingly")

if __name__ == '__main__':
    unittest.main()
