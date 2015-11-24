__author__ = 'mingles'
from flask_restful import fields

lock_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'owner_id': fields.Integer,
    'requested_open':   fields.Boolean,
    'actually_open':   fields.Boolean,
}

lock_fields_with_access = {
    'id':   fields.Integer,
    'name': fields.String,
    'owner_id': fields.Integer,
    'requested_open':   fields.Boolean,
    'actually_open':   fields.Boolean,
    'has_access':   fields.Boolean,
}

user_fields = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'active':   fields.Boolean,
    'is_friend': fields.Boolean,
}

user_fields_with_locks = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'active':   fields.Boolean,
    'is_friend': fields.Boolean,
    'your_locks': fields.List(fields.Nested(lock_fields_with_access)),
}

friend_fields = {
    'id':   fields.Integer,
    'friend': fields.Integer,
}