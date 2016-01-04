__author__ = 'mingles'

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


def is_user_in_db(user):
    email = User.query.filter_by(email=user)
    if email.count() > 0:
        return True
    else:
        return False


def add_related_locks(users, request):
    """
    For each friend, add all the locks that they are members of and you are the owner of
    :param request: the request object from the view
    :param users: the users to add locks to
    """
    my_id = User.query.filter_by(email=request.authorization.username).first().id

    _u1 = aliased(User, name='_u1')
    _u2 = aliased(User, name='_u2')
    _ul = aliased(UserLock, name='_ul')
    _f1 = aliased(Friend, name='_f1')
    _f2 = aliased(Friend, name='_f2')
    _l = aliased(Lock, name='_l')

    # Get all locks I have access to
    my_locks_subquery = db.session.query(_l.id).filter(
        db.session.query(_ul).filter(
            _ul.is_owner,
            _ul.user_id == my_id,
            _ul.lock_id == _l.id,
        ).exists()
    ).subquery()    
    
    # Get all my friends
    my_friends_subquery = db.session.query(_u1).filter(
        db.session.query(_f1).filter(
            _f1.id == my_id,
            _f1.friend_id == _u1.id
        ).exists()
    ).subquery()

    # Get all the people whose friend I am
    their_friend_subquery = db.session.query(_u2).filter(
        db.session.query(_f2).filter(
            _f2.id == _u2.id,
            _f2.friend_id == my_id
        ).exists()
    ).subquery()
    
    def get_their_locks_has_access(user):
        """
        For a given user, add all the locks that they own and you are a member of.
        :param user: the user to add the locks to
        """
        ul  = aliased(UserLock, name='ul')
        ul2 = aliased(UserLock, name='ul2')
        l = aliased(Lock, name='l')
        # Get all locks they own that I have access to
        return db.session.query(l).filter(
            db.session.query(ul).filter(
                ul.is_owner,
                ul.user_id == user.id,
                ul.lock_id == l.id
            ).exists(),
            db.session.query(ul2).filter(
                ul2.user_id == my_id,
                ul2.lock_id == l.id
            ).exists()
        ).all()

    def get_my_locks_has_access(user):
        """
        For a given user, add all the locks that you own and they are a member of.
        :param user: the user to add the locks to
        """
        ul = aliased(UserLock, name='ul')
        l = aliased(Lock, name='l')
        # Get all locks I own that they have access to
        return db.session.query(l).filter(
            db.session.query(ul).filter(
                ul.user_id == user.id,
                ul.lock_id == l.id
            ).exists(),
            l.id.in_(my_locks_subquery)
        ).all()

    def add_related_locks_for_one_user(user):
        # Get their locks (only ones I have access to)
        their_locks = get_their_locks_has_access(user)

        # Get my locks they have access to
        my_locks = get_my_locks_has_access(user)
        
        return their_locks, my_locks

    if isinstance(users, list):
        for user in users:
            user.their_locks, user.my_locks = add_related_locks_for_one_user(user)
    else:
        users.their_locks, users.my_locks = add_related_locks_for_one_user(users)

    return users

def get_user_id():
    email = request.authorization.username
    user_id = User.query.filter_by(email=email).first().id
    return user_id

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
