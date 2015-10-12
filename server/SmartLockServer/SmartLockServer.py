from flask import Flask, jsonify, make_response
from flask_restful import Resource, Api
from os import environ
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth


app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])


api = Api(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

from models import *

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)



class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}


class Mingles(Resource):
    def get(self):
        return {'mingles': 'legend', 'sam': 'mug'}


class ProtectedResource(Resource):
    """
    This endpoint is protected by basic auth and is only used for testing
    """
    decorators = [auth.login_required]
    def get(self):
        return "Hello", 200


api.add_resource(HelloWorld, '/')
api.add_resource(Mingles, '/mingles')
api.add_resource(ProtectedResource, '/protected-resource')

print(api.endpoints)


if __name__ == '__main__':
    app.run(debug=True)