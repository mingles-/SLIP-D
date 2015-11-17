import unittest
import json

from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestCase(BaseTest):

    def setUp(self):
        super(SmartLockTestCase, self).setUp()

        """Register Lock 1 and open it"""
        self.app.post('/user', data=dict(email="test@mail.com", password="python"))
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=123 , lock_name="123"))
        response = self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)

        """Register Lock 2"""
        self.app.post('/user', data=dict(email="test2@mail.com", password="python"))
        self.app.post('/lock', headers=self.auth_header("test2@mail.com", "python"), data=dict(lock_id=321, lock_name="123"))
        self.assertEqual(200, response.status_code)

    def tearDown(self):
        super(SmartLockTestCase, self).tearDown()


    def test_checkClosedLock(self):
        """Check created Lock is automatically closed"""
        lock_closed = False
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=124, lock_name="123"))
        self.app.get('/lock', headers=self.auth_header("test@mail.com", "python"))

        locks = json.loads((self.app.get('/lock', headers=self.auth_header("test@mail.com", "python"))).data)
        for lock in locks:
            if lock['id'] == 124:
                lock_closed = lock['requested_open']

        self.assertEqual(lock_closed, False)

    def test_bad_credentials(self):
        """Check bad credentials are rejected"""
        response = self.app.get('/lock', headers=self.auth_header("test3@mail.com", "python"))
        self.assertEqual(401, response.status_code)

    def test_bad_lock(self):
        """check bad lock is rejected"""
        response = self.app.get('/check/124', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(404, response.status_code)

    def test_lock_not_owned(self):
        """check lock which isn't owned is rejected"""
        response = self.app.get('/open/321', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(405, response.status_code)


if __name__ == '__main__':
    unittest.main()
