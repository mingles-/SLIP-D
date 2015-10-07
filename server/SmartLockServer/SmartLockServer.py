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

api.add_resource(HelloWorld, '/')
api.add_resource(Mingles, '/mingles')



if __name__ == '__main__':
    app.run(debug=True)