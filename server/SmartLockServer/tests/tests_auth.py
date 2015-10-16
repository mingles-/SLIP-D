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

    def test_open_lock_good(self):
        """Ensure that good user credentials are accepted with the open lock """
        response = self.app.post('/register-lock/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)
        response = self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_open_lock_bad_id(self):
        """Ensure that good user credentials fail with the an non existing lock"""
        response = self.app.put('/open/124', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(404, response.status_code)

    def test_open_lock_nae_lock(self):
        """Ensure that good user credentials are not accepted without a lock"""
        response = self.app.put('/open/', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(404, response.status_code)

    def test_open_lock_wrong_login(self):
        """Ensure that bad password, but corect username is rejected with correct lock"""
        response = self.app.put('/open/123', headers=self.auth_header("test@mail.com", "iscool123"))
        self.assertEqual(401, response.status_code)

    def test_register_success(self):
        """Register to gain access to protected resource"""
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(401, response.status_code)
        response = self.app.post('/register', data=dict(email="test2@mail.com", password="python"))
        self.assertEqual(201, response.status_code)
        response = self.app.get('/protected-resource', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_register_lock_success(self):
        """Register a lock to a user"""
        response = self.app.post('/register-lock/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)
        response = self.app.post('/register-lock/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(401, response.status_code)

if __name__ == '__main__':
    unittest.main()
