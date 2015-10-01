__author__ = 'mingles'

import os
import SmartLockServer
import unittest
import tempfile
import json

class SmartLockTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, SmartLockServer.app.config['DATABASE'] = tempfile.mkstemp()
        SmartLockServer.app.config['TESTING'] = True
        self.app = SmartLockServer.app.test_client()
        # SmartLockServer.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(SmartLockServer.app.config['DATABASE'])


    def test_hello_world(self):
        """Ensure that Hello World end Point works"""
        response = self.app.get('/')
        self.assertEqual({'hello': 'world'}, json.loads(response.data))


if __name__ == '__main__':
    unittest.main()