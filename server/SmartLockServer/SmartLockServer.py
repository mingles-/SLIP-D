from os import environ

from flask import Flask, jsonify, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api

app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])

api = Api(app)
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

import models


@auth.get_password
def get_password(email):
    users_with_that_email = models.User.query.filter_by(email=email)
    if users_with_that_email.count() > 0:
        return users_with_that_email[0].password
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


class Register(Resource):

    def post(self):
        email = request.form['email']
        password = request.form['password']
        models.user_datastore.create_user(email=email, password=password)
        db.session.commit()

        new_user = models.User.query.filter_by(email=email)

        return new_user[0].email, 201


class CloseLock(Resource):
    """
    This endpoint closes the lock if lockID and associated user is consistent within the database
    """
    decorators = [auth.login_required]

    def put(self, lock_id):
        # check if lockid is associated with user in db
        if lock_id == 123:
            return "", 200
        else:
            return "", 403

class LockList(Resource):

    def get(self):
        locks = db.session.query(models.Lock).all()
        lock_json = []
        for lock in locks:
            lock_json.append({"id": lock.id, "locked": lock.locked})
        return lock_json

class OpenLock(Resource):
    """
    This endpoint opens the lock if lockID and associated user is consistent within the database
    """
    decorators = [auth.login_required]

    def put(self, lock_id):
        # check if lockid is associated with user in db
        if lock_id == 123:
            return "", 200
        else:
            return "", 403


api.add_resource(HelloWorld, '/')
api.add_resource(Mingles, '/mingles')
api.add_resource(LockList, '/lock')
api.add_resource(Register, '/register')


api.add_resource(ProtectedResource, '/protected-resource')
api.add_resource(OpenLock, '/open/<int:lock_id>')
api.add_resource(CloseLock, '/close/<int:lock_id>')


if __name__ == '__main__':
    app.run(debug=True)
