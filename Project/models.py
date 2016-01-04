from flask.ext.security import RoleMixin, UserMixin
from flask import request
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import exists, and_
from sqlalchemy.orm import backref

__author__ = 'mingles'

from app import db
from sqlalchemy.orm import aliased

# Define models
role_user = db.Table('role_user',
                     db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                     db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255), unique=False, nullable=False, default="")
    last_name = db.Column(db.String(255), unique=False, nullable=False, default="")
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=role_user,
                            backref=db.backref('users', lazy='dynamic'))
    locks = association_proxy('user_locks', 'lock')

    @hybrid_property
    def name(self):
        return '{} {}'.format(self.first_name,self.last_name)
    
    @hybrid_property
    def is_friend(self):
        my_id = User.query.filter_by(email=request.authorization.username).first().id
        return db.session.query(exists().where(and_(Friend.id == my_id, Friend.friend_id == self.id))).scalar()
    

class UserLock(db.Model):
    __tablename__ = 'user_lock'
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    lock_id = db.Column(db.Integer(), db.ForeignKey('lock.id'), primary_key=True)
    is_owner = db.Column(db.Boolean())
    expiry = db.Column(db.DATE(), nullable=True)
    user = db.relationship(User, backref=backref("user_locks", cascade="all, delete-orphan"))
    lock = db.relationship("Lock")

    def __init__(self, user, lock, is_owner, expiry=None):
        self.user = user
        self.lock = lock
        self.is_owner = is_owner
        self.expiry = expiry


class Friend(db.Model):
    __tablename__ = 'friend'
    id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)
    friend_id = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key=True)


class Lock(db.Model):
    __tablename__ = 'lock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, default="")
    # this is true when app requests lock to be open
    requested_open = db.Column(db.Boolean())
    # this is true when the lock says it is open
    actually_open = db.Column(db.Boolean())

    @hybrid_property
    def owner_id(self):
        return UserLock.query.filter_by(lock_id=self.id, is_owner=True).first().user_id

    @hybrid_property
    def friends(self):
        u = aliased(User, name='u')
        ul = aliased(UserLock, name='ul')
        return db.session.query(u).filter(
            db.session.query(ul).filter(
                ul.user_id == u.id,
                ul.lock_id == self.id
            ).exists()
        ).all()

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
