import unittest
import json

from Project.tests.base_test import BaseTest

__author__ = 'Sam Davies'


class OpenWaitingDoneTestCase(BaseTest):

    def setUp(self):
        self.app.post('/user', data=dict(email="test", password="python"))
        self.app.post('/lock', headers=self.auth_header("test", "python"), data=dict(lock_id=124, lock_name="123"))

    def test_open_waiting_done(self):
        """ Play out a full senario of opening a lock, waiting for it to be acked and successfully acked """
        # actually_open = False
        # requested_open = False

        # Lock polls api im_closed and is NOT asked to open
        response = self.app.get('/im_closed/134', data=dict(email="test", password="python"))
        self.assertEqual(202, response.status_code)

        # App requests api to open lock
        # requested_open = True
        response = self.app.get('/open/134', data=dict(email="test", password="python"))
        self.assertEqual(response.content['requested_open'], True)
        self.assertEqual(response.content['actually_open'], False)

        # App polls api and responds actually_open false
        response = self.app.get('/lock/134', data=dict(email="test", password="python"))
        self.assertEqual(response.content['requested_open'], True)
        self.assertEqual(response.content['actually_open'], False)

        # Lock polls im_closed and is asked to open
        response = self.app.get('/im_closed/134', data=dict(email="test", password="python"))
        self.assertEqual(200, response.status_code)

        # Lock polls im_open
        response = self.app.get('/im_open/134', data=dict(email="test", password="python"))

        # actually_open = True, requested_open = False
        # App polls api and responds actually_open true
        response = self.app.get('/lock/134', data=dict(email="test", password="python"))
        self.assertEqual(response.content['requested_open'], False)
        self.assertEqual(response.content['actually_open'], True)
        
        # short time later the lock closes
        response = self.app.get('/im_closed/134', data=dict(email="test", password="python"))
        self.assertEqual(202, response.status_code)

        # check at the end that the state is back to normal
        response = self.app.get('/lock/134', data=dict(email="test", password="python"))
        self.assertEqual(response.content['requested_open'], False)
        self.assertEqual(response.content['actually_open'], False)


if __name__ == '__main__':
    unittest.main()