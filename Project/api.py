from functools import wraps

from flask import request, Response
from flask.ext.security.utils import encrypt_password, verify_password
import sys
from sqlalchemy import exists, and_
from sqlalchemy.orm import aliased

from Project import models, serialisers
from Project.app import db, app
from Project.auth import user_datastore
from flask.ext.restplus import Api, Resource, fields, marshal_with

from Project.models import User, UserLock, Lock, Friend

sys.setrecursionlimit(1000000)

api = Api(app)
ns = api.namespace('smartlock', description='User operations')


def check_auth(email, password):
    """
    This function is called to check if a username & password combination is valid.
    """
    users_with_that_email = User.query.filter_by(email=email)
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


def add_is_friend(users, request):
    def get_is_friend(user_id, friend_id):
        return db.session.query(exists().where(and_(Friend.id == user_id, Friend.friend_id == friend_id))).scalar()

    my_id = User.query.filter_by(email=request.authorization.username).first().id

    if isinstance(users, list):
        for user in users:
            user.is_friend = get_is_friend(my_id, user.id)
    else:
        get_is_friend(my_id, users.id)

    return users


@api.doc(responses={200: 'Successfully pinged API'})
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

@api.doc(responses={200: 'Successfully logged in '})
class ProtectedResource(Resource):
    """
    This endpoint is protected by basic auth and is only used for testing
    """
    decorators = [requires_auth]

    def get(self):
        return {"message": "Hello"}, 200

@api.doc(responses={200: 'Lock Successfully Opened', 401: 'User has no permission to open lock'})
class OpenLock(Resource):
    """
    This endpoint opens the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]
    @marshal_with(serialisers.lock_fields)
    def put(self, lock_id):
        """Opens a Lock"""
        return change_lock_state(lock_id, True)


class CloseLock(Resource):
    """
    This endpoint closes the lock if lockID and associated user is consistent within the database
    """
    decorators = [requires_auth]

    @marshal_with(serialisers.lock_fields)
    def put(self, lock_id):
        """Closes a Lock"""
        return change_lock_state(lock_id, False)


def is_user_in_db(user):
    email = User.query.filter_by(email=user)
    if email.count() > 0:
        return True
    else:
        return False


def change_lock_state(lock_id, new_state):

    if lock_id is not None:

        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id
        users_with_lock = UserLock.query.filter_by(lock_id=lock_id)

        if users_with_lock is not None:
            lock_row = Lock.query.filter_by(id=lock_id).first()
            for user_with_lock in users_with_lock:

                if user_id == user_with_lock.user_id:
                    lock_row.requested_open = new_state
                    db.session.commit()
                    return Lock.query.filter_by(id=lock_id).first(), 200

            return Lock.query.filter_by(id=lock_id).first(), 401

    return None, 404


class UserList(Resource):
    @requires_auth
    @marshal_with(serialisers.user_fields)
    def get(self):
        """Gets list of users """
        users = db.session.query(User)

        # optionally allow the user list to be filter by lock id
        lock_id = request.args.get('lock_id')
        if lock_id:
            users = users.filter(User.locks.any(id=lock_id))

        users = add_is_friend(users.all(), request)

        return users, 200

    @marshal_with(serialisers.user_fields)
    def post(self):
        """Register User"""
        email = request.form['email']
        password = encrypt_password(request.form['password'])
        first_name = "" + request.form['first_name']
        last_name = "" + request.form['last_name']

        if not is_user_in_db(email):
            user_datastore.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            db.session.commit()
            new_user = User.query.filter_by(email=email).first()
            return new_user, 201

        return User.query.filter_by(email=email).first(), 406


class UserDetail(Resource):
    decorators = [requires_auth]
    @marshal_with(serialisers.user_fields_with_locks)
    def get(self, user_id):
        """ Gets Friend Information """
        user_exists = db.session.query(exists().where(User.id == user_id)).scalar()
        user = User.query.filter_by(id=user_id).first()
        if user_exists:
            user = add_related_locks(user, request)
            user = add_is_friend(user, request)
            return user, 200
        else:
            return user_id, 404


class Me(Resource):
    decorators = [requires_auth]
    # return user information
    @marshal_with(serialisers.user_fields)
    def get(self):
        email = request.authorization.username
        user_exists = User.query.filter_by(email=email)
        if user_exists > 0:
            return add_is_friend(user_exists.first(), request), 200
        else:
            return email, 404


class LockDetail(Resource):
    decorators = [requires_auth]

    @marshal_with(serialisers.lock_fields)
    def get(self, lock_id):
        lock = Lock.query.filter_by(id=lock_id).first()
        return lock


class LockList(Resource):
    decorators = [requires_auth]
    # gets list of all locks
    @marshal_with(serialisers.lock_fields)
    def get(self):
        email = request.authorization.username
        user = User.query.filter_by(email=email).first()
        return list(user.locks)


    # register lock
    @marshal_with(serialisers.lock_fields)
    def post(self):
        lock_name = request.form['lock_name']
        lock_id = request.form['lock_id']
        email = request.authorization.username
        # add in many to many table
        database_lock_id = Lock.query.filter_by(id=lock_id)

        if database_lock_id.count() > 0:
            return lock_id, 406
        else:
            user = User.query.filter_by(email=email).first()
            lock = Lock(id=lock_id, name=lock_name, requested_open=False, actually_open=False)

            user_lock = UserLock(user, lock, is_owner=True)

            db.session.add(lock)
            db.session.add(user_lock)
            db.session.commit()
            lock = Lock.query.filter_by(id=lock_id)
            return lock.first(), 201


class Status(Resource):
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:
            state = database_lock_id.first().requested_open
            if state:
                return state, 202
            else:
                return state, 200
        else:
            return False, 404


def add_related_locks(users, request):
    """
    For each friend, add all the locks that they are members of and you are the owner of
    :param request: the request object from the view
    :param users: the users to add locks to
    """
    my_id = User.query.filter_by(email=request.authorization.username).first().id
    # get all he locks where I am the owner
    ul1 = aliased(UserLock, name='ul1')
    ul2 = aliased(UserLock, name='ul2')
    l1 = aliased(Lock, name='l1')
    l2 = aliased(Lock, name='l2')

    my_locks_subquery = db.session.query(l1.id).filter(
        db.session.query(ul1).filter(
            ul1.is_owner,
            ul1.user_id == my_id,
            ul1.lock_id == l1.id
        ).exists()
    ).subquery()

    def add_your_locks(user):
        """
        For a give user, add all the locks that you own and they are a member of.
        :param user: the user to add the locks to
        """
        return db.session.query(l2).filter(
            db.session.query(ul2).filter(
                ul2.user_id == user.id,
                ul2.lock_id == l1.id
            ).exists(),
            l2.id.in_(my_locks_subquery)
        ).all()

    if isinstance(users, list):
        for user in users:
            user.your_locks = add_your_locks(user)
    else:
        users.your_locks = add_your_locks(users)

    return users


class FriendList(Resource):
    decorators = [requires_auth]

    @marshal_with(serialisers.user_fields)
    def post(self):

        friend_id = int(request.form['friend_id'])
        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        existing_friend = Friend.query.filter_by(id=user_id, friend_id=friend_id)
        friend_user_row = User.query.filter_by(id=friend_id).first()

        if (not existing_friend.count() > 0) and friend_id != user_id:

            friendship = Friend(id=user_id, friend_id=friend_id)

            db.session.add(friendship)
            db.session.commit()

            return add_is_friend(friend_user_row, request), 201

        else:

            return add_is_friend(friend_user_row, request), 401




    @marshal_with(serialisers.user_fields_with_locks)
    def get(self):

        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id

        users = self.get_users_friends(user_id)
        users = add_related_locks(users, request)
        users = add_is_friend(users, request)

        return users, 200

    # @marshal_with(serialisers.user_fields)
    def delete(self):

        email = request.authorization.username
        user_id = User.query.filter_by(email=email).first().id
        friend_id = int(request.args['friend_id'])
        existing_friend = Friend.query.filter_by(id=user_id, friend_id=friend_id)

        if existing_friend.count() > 0:

            db.session.query(Friend).filter(Friend.id == user_id,
                                                   Friend.friend_id == friend_id).delete()
            db.session.commit()

            return add_is_friend(self.get_users_friends(user_id), request), 200

        else:

            # deleting friendship with an id which isn't a friend
            return self.get_users_friends(user_id), 401

    @staticmethod
    def get_users_friends(user_id):
        friend_ids = Friend.query.filter_by(id=user_id)
        friend_user_rows = []
        for friend_id in friend_ids:
            friend_user_rows.append(User.query.filter_by(id=friend_id.friend_id).first())

        return friend_user_rows


class ImOpen(Resource):
    # im open
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:

            lock = database_lock_id.first()
            if lock.requested_open is True and lock.actually_open is False: # Open is requested, Lock is closed on server, Lock is open
                lock.actually_open  = True # Open the lock
                db.session.commit()
                return lock.actually_open, 202
            elif lock.requested_open is True and lock.actually_open is True: # Open is requested, Lock is open on server, Lock is open
                return lock.actually_open, 202
            elif lock.requested_open is False and lock.actually_open is True: # Close is requested, Lock is open on server, Lock is open
                return lock.actually_open, 200
            elif lock.requested_open is False and lock.actually_open is False: # Close is requested, Lock is closed on server, Lock is open
                lock.actually_open = True # Open the lock
                db.session.commit()
                return lock.actually_open, 200
        else:
            return False, 404


class ImClosed(Resource):
    # im closed
    def get(self, lock_id):
        database_lock_id = Lock.query.filter_by(id=lock_id)
        if database_lock_id.count() > 0:

            lock = database_lock_id.first()
            if lock.requested_open is False and lock.actually_open is True: # Close is requested, Lock is open on server, Lock is closed
                lock.actually_open  = False # Open the lock
                db.session.commit()
                return lock.actually_open, 202
            elif lock.requested_open is False and lock.actually_open is False: # Close is requested, Lock is closed on server, Lock is closed
                return lock.actually_open, 202
            elif lock.requested_open is True and lock.actually_open is False: # Open is requested, Lock is closed on server, Lock is closed
                return lock.actually_open, 200
            elif lock.requested_open is True and lock.actually_open is True: # Open is requested, Lock is open on server, Lock is closed
                lock.actually_open = False # Open the lock
                db.session.commit()
                return lock.actually_open, 200
        else:
            return False, 404


def get_user_id():
    email = request.authorization.username
    user_id = User.query.filter_by(email=email).first().id
    return user_id


class FriendLocks(Resource):
    decorators = [requires_auth]

    # add a friend to one of your locks
    def post(self):
        friend_id = request.form['friend_id']
        lock_id = request.form['lock_id']
        user_id = get_user_id()

        are_friends = Friend.query.filter_by(id=user_id, friend_id=friend_id).count() > 0


        lock_exists = UserLock.query.filter_by(user_id=user_id, lock_id=lock_id)
        if lock_exists.count() > 0:
            user_owns_lock = lock_exists.first().is_owner
        else:
            user_owns_lock = False

        if are_friends is True and user_owns_lock is True:
            user = User.query.filter_by(id=friend_id).first()
            lock = Lock.query.filter_by(id=lock_id).first()
            user_lock = UserLock(user, lock, is_owner=False)
            db.session.add(user_lock)
            db.session.commit()
            return True, 201
        else:
            return False, 400

    def delete(self):
        friend_id = request.args['friend_id']
        lock_id = request.args['lock_id']
        user_id = get_user_id()

        lock_exists = UserLock.query.filter_by(user_id=user_id, lock_id=lock_id)
        if lock_exists.count() > 0:
            user_owns_lock = lock_exists.first().is_owner
        else:
            user_owns_lock = False

        friend_assigned_to_lock = UserLock.query.filter_by(user_id=friend_id, lock_id=lock_id, is_owner=False).count() > 0

        if friend_assigned_to_lock and user_owns_lock:

            db.session.query(UserLock).filter(UserLock.user_id == friend_id,
                                                   UserLock.lock_id == lock_id).delete()
            db.session.commit()

            return True, 200
        else:
            return False, 401



# testing endpoints
api.add_resource(HelloWorld, '/hello')
api.add_resource(ProtectedResource, '/protected-resource')
# new endpoints

api.add_resource(ImOpen, '/im-open/<int:lock_id>')
api.add_resource(ImClosed, '/im-closed/<int:lock_id>')
api.add_resource(FriendLocks, '/friend-lock')

api.add_resource(UserList, '/user')
api.add_resource(Me, '/me')
api.add_resource(UserDetail, '/user/<int:user_id>')
api.add_resource(LockList, '/lock')
api.add_resource(LockDetail, '/lock/<int:lock_id>')
api.add_resource(OpenLock, '/open/<int:lock_id>')
api.add_resource(CloseLock, '/close/<int:lock_id>')
api.add_resource(Status, '/status/<int:lock_id>')
api.add_resource(FriendList, '/friend')


