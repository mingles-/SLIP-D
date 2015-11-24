import unittest
import json
from Project.models import User
from Project.tests.base_test import BaseTest

__author__ = 'mingles'


class SmartLockTestFriend(BaseTest):

    def setUp(self):
        super(SmartLockTestFriend, self).setUp()
        user_reg = self.register_user(username="test@mail.com", password="python")
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=123, lock_name="123"))

        user2_reg = self.register_user(username="test2@mail.com", password="python")
        self.app.post('/lock', headers=self.auth_header("test2@mail.com", "python"), data=dict(lock_id=456, lock_name="456"))

        user3_reg = self.register_user(username="test3@mail.com", password="python")
        self.app.post('/lock', headers=self.auth_header("test3@mail.com", "python"), data=dict(lock_id=789, lock_name="789"))

        self.user_id = json.loads(user_reg.data)['id']
        self.user2_id = json.loads(user2_reg.data)['id']
        self.user3_id = json.loads(user3_reg.data)['id']

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
        response = self.app.delete('/friend', headers=self.auth_header("test@mail.com", "python"), query_string=dict(friend_id=self.user2_id))
        friend_id = json.loads(response.data)
        self.assertEqual(friend_id, [])

    def test_add_friend_to_lock(self):
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)

    def test_fail_adding_non_friend(self):
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user3_id, lock_id=123))
        self.assertEqual(response.status_code, 400)

    def test_fail_not_own_lock(self):
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=456))
        self.assertEqual(response.status_code, 400)

    def test_add_and_remove_friend_to_lock(self):
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)
        response = self.app.delete('/friend-lock', headers=self.auth_header("test@mail.com", "python"), query_string=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 200)

    def test_check_friend_open_lock(self):

        # fail to open lock on friends account
        response = self.app.put('/open/123', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(401, response.status_code)

        # add friend
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)

        # successfully open lock as friend
        response = self.app.put('/open/123', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(200, response.status_code)

        # delete friend
        response = self.app.delete('/friend-lock', headers=self.auth_header("test@mail.com", "python"), query_string=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 200)

        # fail to open lock on friends account
        response = self.app.put('/open/123', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(401, response.status_code)

    def test_lock_owner(self):

        # add friend
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)

        response = self.app.get('/lock/123', headers=self.auth_header("test2@mail.com", "python") )
        self.assertEqual(self.user_id, json.loads(response.data)['owner_id'])

        # successfully open lock as friend
        response = self.app.put('/open/123', headers=self.auth_header("test2@mail.com", "python"))
        self.assertEqual(200, response.status_code)

    def test_friend_list_with_your_locks(self):
        self.app.post('/lock', headers=self.auth_header("test@mail.com", "python"), data=dict(lock_id=124, lock_name="124"))
        # add friend
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)

        response = self.app.get('/friend', headers=self.auth_header("test@mail.com", "python"))
        data = json.loads(response.data)
        self.assertEqual(2, len(data[0]['your_locks']))
        self.assertTrue(data[0]['your_locks'][0]['has_access'])
        self.assertFalse(data[0]['your_locks'][1]['has_access'])

    def test_friend_detail_with_your_locks(self):
        # add friend
        response = self.app.post('/friend-lock', headers=self.auth_header("test@mail.com", "python"), data=dict(friend_id=self.user2_id, lock_id=123))
        self.assertEqual(response.status_code, 201)

        response = self.app.get('/user/{0}'.format(self.user2_id) , headers=self.auth_header("test@mail.com", "python"))
        data = json.loads(response.data)
        self.assertEqual(123, data['your_locks'][0]['id'])
        self.assertNotEqual(data['is_friend'], None)


if __name__ == '__main__':
    unittest.main()
