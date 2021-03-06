import unittest
import json

from Project.tests.base_test import BaseTest

__author__ = 'Sam Davies'


class OpenWaitingDoneTestCase(BaseTest):

    def setUp(self):
        super(OpenWaitingDoneTestCase, self).setUp()
        self.register_user(username="test", password="python")
        self.app.post('/lock', headers=self.auth_header("test", "python"), data=dict(lock_id=134, lock_name="134"))

    def test_open_waiting_done(self):
        """ Play out a full senario of opening a lock, waiting for it to be acked and successfully acked """
        # actually_open = False
        # requested_open = False

        # Lock polls api im_closed and is NOT asked to open
        response = self.app.get('/im-closed/134', headers=self.auth_header("test", "python"))
        self.assertEqual(202, response.status_code)

        # App requests api to open lock
        # requested_open = True
        response = self.app.put('/open/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)["requested_open"], True)
        self.assertEqual(json.loads(response.data)['actually_open'], False)

        # App polls api and responds actually_open false
        response = self.app.get('/lock/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)["requested_open"], True)
        self.assertEqual(json.loads(response.data)['actually_open'], False)

        # Lock polls im_closed and is asked to open
        response = self.app.get('/im-closed/134', headers=self.auth_header("test", "python"))
        self.assertEqual(200, response.status_code)

        # Lock polls im_open
        response = self.app.get('/im-open/134', headers=self.auth_header("test", "python"))
        self.assertEqual(202, response.status_code)

        # actually_open = True, requested_open = True
        # App polls api and responds actually_open true
        response = self.app.get('/lock/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)['requested_open'], True)
        self.assertEqual(json.loads(response.data)['actually_open'], True)

        # Lock polls im_open and is told all is fine
        response = self.app.get('/im-open/134', headers=self.auth_header("test", "python"))
        self.assertEqual(202, response.status_code)

        # App requests api to close lock
        # requested_open = False
        response = self.app.put('/close/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)["requested_open"], False)
        self.assertEqual(json.loads(response.data)['actually_open'], True)

        # short time later the lock is told to close
        response = self.app.get('/im-open/134', headers=self.auth_header("test", "python"))
        self.assertEqual(200, response.status_code)

        # lock is still open
        response = self.app.get('/lock/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)["requested_open"], False)
        self.assertEqual(json.loads(response.data)['actually_open'], True)

        response = self.app.get('/im-closed/134', headers=self.auth_header("test", "python"))
        self.assertEqual(202, response.status_code)

        # check at the end that the state is back to normal
        response = self.app.get('/lock/134', headers=self.auth_header("test", "python"))
        self.assertEqual(json.loads(response.data)['requested_open'], False)
        self.assertEqual(json.loads(response.data)['actually_open'], False)


if __name__ == '__main__':
    unittest.main()