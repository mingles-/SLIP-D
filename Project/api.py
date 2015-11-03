from functools import wraps

from flask import request, Response
from flask.ext.security.utils import encrypt_password, verify_password
from flask_restful import Resource

from Project import models, serialisers
from Project.app import db, app
from Project.auth import user_datastore
from flask_restful import Api, marshal_with


api = Api(app)


def check_auth(email, password):
    """
    This function is called to check if a username & password combination is valid.
    """
    users_with_that_email = models.User.query.filter_by(email=email)
    if users_with_that_email.count() > 0:
        db_password = users_with_that_email[0].password
        return verify_password(password, db_password)
    return False


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
        return {"message": "Hello"}, 200


class OpenLock(Resource):
    """
    This endpoint opens the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    def put(self, lock_id):
        return change_lock_state(lock_id, False)


class CloseLock(Resource):
    """
    This endpoint closes the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    def put(self, lock_id):
        return change_lock_state(lock_id, True)


def is_user_in_db(user):
    email = models.User.query.filter_by(email=user)
    if email.count() > 0:
        return True
    else:
        return False


@requires_auth
def change_lock_state(lock_id, new_state):

    if lock_id is not None:

        email = request.authorization.username
        user_id = models.User.query.filter_by(email=email).first().id
        users_with_lock = models.UserLock.query.filter_by(lock_id=lock_id)

        if users_with_lock is not None:
            lock_row = models.Lock.query.filter_by(id=lock_id).first()
            for user_with_lock in users_with_lock:
                if user_id == user_with_lock.user_id:
                    lock_row.locked = new_state
                    db.session.commit()
                    return lock_id, 200
                else:
                    return lock_id, 401
    return lock_id, 404


class UserList(Resource):
    # gets list of users
    @requires_auth
    @marshal_with(serialisers.user_fields)
    def get(self):
        users = models.User.query.all()
        return users

    # register user
    @marshal_with(serialisers.user_fields)
    def post(self):
        email = request.form['email']
        password = encrypt_password(request.form['password'])

        if not is_user_in_db(email):
            user_datastore.create_user(email=email, password=password)
            db.session.commit()
            new_user = models.User.query.filter_by(email=email).first()
            return new_user, 201

        return models.User.query.filter_by(email=email).first(), 406


class UserDetail(Resource):
    decorators = [requires_auth]
    # return user information
    @marshal_with(serialisers.user_fields)
    def get(self, user_id):
        user_exists = models.User.query.filter_by(id=user_id)
        if user_exists > 0:
            return user_exists.first(), 200
        else:
            return user_id, 404


class LockList(Resource):
    decorators = [requires_auth]
    # gets list of all locks
    @marshal_with(serialisers.lock_fields)
    def get(self):
        locks = models.Lock.query.all()
        return locks

    # register lock
    @marshal_with(serialisers.lock_fields)
    def post(self):
        lock_name = request.form['lock_name']
        lock_id = request.form['lock_id']
        email = request.authorization.username
        # add in many to many table
        database_lock_id = models.Lock.query.filter_by(id=lock_id)

        if database_lock_id.count() > 0:
            return lock_id, 406
        else:
            user = models.User.query.filter_by(email=email).first()
            lock = models.Lock(id=lock_id, name=lock_name, locked=True)


            user_lock = models.UserLock(is_owner=True)
            user_lock.lock = lock
            user.locks.append(user_lock)


            db.session.add(lock)
            db.session.add(user_lock)
            db.session.commit()
            lock = models.Lock.query.filter_by(id=lock_id)
            return lock.first(), 201




#
#
# class FriendList(Resource):
#     def get(self):
#     def post(self):
#
# class FriendDetail(Resource):
#     def delete(self):



# testing endpoints
api.add_resource(HelloWorld, '/')
api.add_resource(ProtectedResource, '/protected-resource')

# new endpoints
api.add_resource(UserList, '/user')
api.add_resource(UserDetail, '/user/<int:user_id>')
api.add_resource(LockList, '/lock')
api.add_resource(OpenLock, '/open', '/open/<int:lock_id>')
api.add_resource(CloseLock, '/close', '/close/<int:lock_id>')

