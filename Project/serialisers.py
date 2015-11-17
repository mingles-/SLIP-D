__author__ = 'mingles'
from flask_restful import fields, marshal_with

user_fields = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first_name':   fields.String,
    'last_name':   fields.String,
    'active':   fields.Boolean,
}

lock_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'requested_open':   fields.Boolean,
    'actually_open':   fields.Boolean,
}