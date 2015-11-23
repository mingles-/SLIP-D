from flask import request
from sqlalchemy import and_

from Project.models import Friend, User

__author__ = 'mingles'
from flask_restful import fields

user_fields = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'active':   fields.Boolean,
    'is_friend': fields.Boolean,
}

lock_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'owner_id': fields.Integer,
    'requested_open':   fields.Boolean,
    'actually_open':   fields.Boolean,
}

friend_fields = {
    'id':   fields.Integer,
    'friend': fields.Integer,
}