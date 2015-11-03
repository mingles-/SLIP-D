__author__ = 'mingles'
from flask_restful import fields, marshal_with

user_fields = {
    'id':   fields.Integer,
    'email':   fields.String,
    'first name':   fields.String,
    'last name':   fields.String,
    'active':   fields.Boolean,
}

lock_fields = {
    'id':   fields.Integer,
    'name': fields.String,
    'locked':   fields.Boolean,
}