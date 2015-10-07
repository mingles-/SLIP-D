from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)


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