import os
import unittest
import tempfile
from base64 import b64encode

from Project.main import app, db
from Project.main import User, Lock, Role, role_user, user_lock

__author__ = 'mingles'


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        User.query.delete()
        Lock.query.delete()
        Role.query.delete()
        role_user.delete()
        user_lock.delete()
        db.session.commit()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

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
