import unittest
import json
from Project.models import Lock
from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestLock(BaseTest):

    def setUp(self):
        super(SmartLockTestLock, self).setUp()
        self.register_user(username="test@mail.com", password="python")
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=123, lock_name="123"))

    def tearDown(self):
        super(SmartLockTestLock, self).tearDown()

    def test_register_lock_success(self):
        """Successfully register a lock"""
        response = self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=124, lock_name="123"))
        self.assertEqual(201, response.status_code)
        self.assertEqual(json.loads(response.data)["id"], 124)
        self.assertEqual(json.loads(response.data)["requested_open"], False)

    def test_register_lock_bad_auth(self):
        """Fail an unauthorized user """
        response = self.app.post('/lock', headers=self.auth_header("", ""), data=dict(lock_id=124, lock_name="123"))
        self.assertEqual(401, response.status_code)

    def test_already_registered_lock(self):
        """Attempt to register an already registered lock"""
        response = self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=123, lock_name="123"))
        self.assertEqual(406, response.status_code)

    def test_already_registered_lock_same_user(self):
        """Attempt to register an already registered lock with a different user"""
        self.register_user(username="test2@mail.com", password="python")
        response = self.app.post('/lock', headers=self.auth_header("test2@mail.com", "python"), data=dict(lock_id=123, lock_name="123"))
        self.assertEqual(406, response.status_code)

    def test_get_list_of_locks(self):
        """gets a list of all locks for a user"""
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=124, lock_name="123"))
        response = self.app.get('/lock', headers=self.auth_header("test@mail.com", "python"))
        lock_list = json.loads(response.data)
        self.assertEqual(lock_list[0]["id"], 123)
        self.assertEqual(lock_list[1]["id"], 124)

    def test_open_lock_good(self):
        """Ensure that good user credentials are accepted with the open lock """
        response = self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_open_lock_bad_id(self):
        """Ensure that good user credentials fail with the an non existing lock"""
        response = self.app.put('/open/124', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(401, response.status_code)

    def test_open_lock_nae_lock(self):
        """Ensure that good user credentials are not accepted without a lock"""
        response = self.app.put('/open/', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(404, response.status_code)

    def test_open_lock_not_owned(self):
        """Attempt to open an existing lock not owned by user"""
        self.register_user(username="test2@mail.com", password="python")
        self.app.post('/lock', headers=self.auth_header("test2@mail.com", "python"), data=dict(lock_id=124, lock_name="123"))
        response = self.app.put('/open/124', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(401, response.status_code)

    def test_open_and_close_lock(self):
        self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        database_lock_id = Lock.query.filter_by(id=123).first()
        self.assertEqual(database_lock_id.requested_open, True)

    def test_status_closed(self):
        """Check status of locked lock"""
        response = self.app.get('/status/123')
        self.assertEqual(response.data, "false\n")

    def test_status_open(self):
        """Check status of unlocked lock"""
        self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        response = self.app.get('/status/123')
        self.assertEqual(response.data, "true\n")

    def test_status_open_closed(self):
        """Check status of an unlocked, then relocked lock"""
        response = self.app.put('/open/123', headers=self.auth_header("test@mail.com", "python"))
        self.assertEqual(json.loads(response.data)["requested_open"], True)


if __name__ == '__main__':
    unittest.main()
