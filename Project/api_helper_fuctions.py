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


def add_is_friend(users, request):
    def get_is_friend(user_id, friend_id):
        return db.session.query(exists().where(and_(Friend.id == user_id, Friend.friend_id == friend_id))).scalar()

    my_id = User.query.filter_by(email=request.authorization.username).first().id

    if isinstance(users, list):
        for user in users:
            user.is_friend = get_is_friend(my_id, user.id)
    else:
        users.is_friend = get_is_friend(my_id, users.id)

    return users


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

    def get_your_locks_has_access(user):
        """
        For a give user, add all the locks that you own and they are a member of.
        :param user: the user to add the locks to
        """
        return db.session.query(l2).filter(
            db.session.query(ul2).filter(
                ul2.user_id == user.id,
                ul2.lock_id == l2.id
            ).exists(),
            l2.id.in_(my_locks_subquery)
        ).all()

    def get_your_locks_not_has_access(user):
        """
        For a give user, add all the locks that you own and they are NOT a member of.
        :param user: the user to add the locks to
        """
        return db.session.query(l2).filter(
            ~db.session.query(ul2).filter(
                ul2.user_id == user.id,
                ul2.lock_id == l2.id
            ).exists(),
            l2.id.in_(my_locks_subquery)
        ).all()

    def add_has_access(locks, has_access):
        for lock in locks:
            lock.has_access = has_access
        return locks

    def add_related_locks_for_one_user(user):
        # get has access locks
        your_locks = get_your_locks_has_access(user)
        your_locks = add_has_access(your_locks, True)

        # get all locks without access
        my_locks = get_your_locks_not_has_access(user)
        my_locks = add_has_access(my_locks, False)

        return your_locks + my_locks

    if isinstance(users, list):
        for user in users:
            user.your_locks = add_related_locks_for_one_user(user)
    else:
        users.your_locks = add_related_locks_for_one_user(users)

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
