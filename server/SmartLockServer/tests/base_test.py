import os
import SmartLockServer
import unittest
import tempfile
import models
from base64 import b64encode

__author__ = 'mingles'


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db_fd, SmartLockServer.app.config['DATABASE'] = tempfile.mkstemp()
        SmartLockServer.app.config['TESTING'] = True
        self.app = SmartLockServer.app.test_client()
        models.User.query.delete()
        models.Lock.query.delete()
        models.Role.query.delete()
        models.role_user.delete()
        models.user_lock.delete()
        SmartLockServer.db.session.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(SmartLockServer.app.config['DATABASE'])


    def auth_header(self, username, password):
        """
        :param username: the user to log in's username
        :param password: the user to log in's password
        :return: the authentication header as a string string
        """
        return {
            'Authorization': 'Basic ' + b64encode("{0}:{1}".format(username, password))
        }

if __name__ == '__main__':
    unittest.main()
