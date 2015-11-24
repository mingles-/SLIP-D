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

from api_hardware import *
from api_locks import *
from api_users import *
from api_friends import *


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


# testing endpoints
api.add_resource(HelloWorld, '/hello')
api.add_resource(ProtectedResource, '/protected-resource')

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


