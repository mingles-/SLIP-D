__author__ = 'mingles'
from flask_restful import fields

user_fields = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'name':   fields.String,
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

lock_fields_with_friends = {
    'id':   fields.Integer,
    'name': fields.String,
    'owner_id': fields.Integer,
    'requested_open':   fields.Boolean,
    'actually_open':   fields.Boolean,
    'friends': fields.List(fields.Nested(user_fields)),
}

user_fields_with_locks = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'name':   fields.String,
    'active':   fields.Boolean,
    'is_friend': fields.Boolean,
    'my_locks': fields.List(fields.Nested(lock_fields)),
    'their_locks': fields.List(fields.Nested(lock_fields))
}

friend_fields = {
    'id':   fields.Integer,
    'friend': fields.Integer,
}
