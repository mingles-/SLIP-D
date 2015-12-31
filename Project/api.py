import sys
from Project.app import app
from flask.ext.restplus import Api, fields


sys.setrecursionlimit(1000000)

api = Api(app, version='4.0', title='smartlock', description='API for App Controlled Smartlock',
          default="smartlock")
ns = api.namespace('smartlock', description='User operations')

from api_hardware import *
from api_locks import *
from api_users import *
from api_friends import *


@api.doc(responses={200: 'Successfully pinged API'})
class HelloWorld(Resource):
    def get(self):
        """Testing: Primative GET"""
        return {'hello': 'world'}


@api.doc(responses={200: 'Successfully logged in '})
class ProtectedResource(Resource):
    """
    This endpoint is protected by basic auth and is only used for testing
    """
    decorators = [requires_auth]

    def get(self):
        """Testing: Authentication"""
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


