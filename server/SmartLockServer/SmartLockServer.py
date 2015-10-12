from flask import Flask
from flask.ext.security import SQLAlchemyUserDatastore, Security
from flask_restful import Resource, Api
from os import environ
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])


api = Api(app)
db = SQLAlchemy(app)

from models import *

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)



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
    def get(self):
        return "Hello", 200


api.add_resource(HelloWorld, '/')
api.add_resource(Mingles, '/mingles')
api.add_resource(ProtectedResource, '/protected-resource')


if __name__ == '__main__':
    app.run(debug=True)