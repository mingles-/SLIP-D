import unittest
import json
from Project.models import User
from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestFriend(BaseTest):

    def setUp(self):
        super(SmartLockTestFriend, self).setUp()
        user_reg = self.app.post('/user', data=dict(email="test@mail.com", password="python"))
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=123, lock_name="123"))

        user2_reg = self.app.post('/user', data=dict(email="test2@mail.com", password="python"))
        self.app.post('/lock', headers=self.auth_header("test2@mail.com", "python"), data=dict(lock_id=456, lock_name="456"))

        self.user_id = json.loads(user_reg.data)['id']
        self.user2_id = json.loads(user2_reg.data)['id']

        response = self.app.post('/friend', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id))
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        super(SmartLockTestFriend, self).tearDown()

    def test_already_registered_friend(self):
        response = self.app.post('/friend', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id))
        self.assertEqual(response.status_code, 401)

    def test_reverse_friendship(self):
        response = self.app.post('/friend', headers=self.auth_header("test2@mail.com", "python"), data=dict(friend_id=self.user_id))
        self.assertEqual(response.status_code, 201)


    def test_register_yourself(self):
        response = self.app.post('/friend', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user_id))
        self.assertEqual(response.status_code, 401)

    def test_get_friends(self):
        response = self.app.get('/friend', headers=self.auth_header("test@mail.com", "python"))
        friend_id = json.loads(response.data)[0]['id']
        self.assertEqual(friend_id, self.user2_id)

    def test_delete_friends(self):
        response = self.app.delete('/friend', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id))
        friend_id = json.loads(response.data)
        self.assertEqual(friend_id, [])






if __name__ == '__main__':
    unittest.main()
