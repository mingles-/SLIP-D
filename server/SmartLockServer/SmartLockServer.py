from os import environ

from flask import Flask, jsonify, make_response, request
from flask.ext import restful
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Resource
from flask.ext.security.utils import encrypt_password, verify_password
from functools import wraps
import types


from flask import request, Response


app = Flask(__name__)


app.config.from_object(environ['APP_SETTINGS'])
app.config['SECURITY_PASSWORD_HASH'] = environ.get('SECURITY_PASSWORD_HASH')
app.config['SECURITY_PASSWORD_SALT'] = environ.get('SECURITY_PASSWORD_SALT')

api = restful.Api(app)
db = SQLAlchemy(app)

import models


def api_route(self, *args, **kwargs):
    def wrapper(cls):
        self.add_resource(cls, *args, **kwargs)
        return cls
    return wrapper

api.route = types.MethodType(api_route, api)


def check_auth(email, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    users_with_that_email = models.User.query.filter_by(email=email)
    db_password = ""
    if users_with_that_email.count() > 0:
        db_password = users_with_that_email[0].password

    return verify_password(password, db_password)


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


class HelloWorld(Resource):

    def get(self):
        return {'hello': 'world'}


class ProtectedResource(Resource):
    """
    This endpoint is protected by basic auth and is only used for testing
    """
    decorators = [requires_auth]
    def get(self):
        return "Hello", 200


class Register(Resource):
    """
    This endpoint registers a user's email and password, encrypting the latter in the database.
    """

    def post(self):
        email = request.form['email']
        password = encrypt_password(request.form['password'])
        models.user_datastore.create_user(email=email, password=password)
        db.session.commit()
        new_user = models.User.query.filter_by(email=email)

        return new_user[0].email, 201




class OpenLock(Resource):
    """
    This endpoint opens the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    def put(self, lock_id):

        if lock_id == 123:
            return 200
        elif lock_id is None:
            return lock_id, 404
        else:
            return lock_id, 401


class CloseLock(Resource):
    """
    This endpoint closes the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    def put(self, lock_id):
        # check if lockid is associated with user in db
        if lock_id == 123:
            return "close lock 123", 200
        else:
            return "", 403


class LockList(Resource):

    def get(self):
        locks = db.session.query(models.Lock).all()
        lock_json = []
        for lock in locks:
            lock_json.append({"id": lock.id, "locked": lock.locked})
        return lock_json



api.add_resource(ProtectedResource, '/protected-resource')
api.add_resource(HelloWorld, '/')
api.add_resource(Register, '/register')
api.add_resource(LockList, '/lock')
api.add_resource(OpenLock, '/open', '/open/<int:lock_id>')
api.add_resource(CloseLock, '/close', '/close/<int:lock_id>')


if __name__ == '__main__':
    app.run(debug=True)
