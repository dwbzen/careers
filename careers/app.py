from telnetlib import GA
from flask import Flask, Response
from flask_restful import reqparse, abort, Api, Resource
from server.game import Game

app = Flask(__name__)
api = Api(app)

# @app.route('/')
# def default():
#     return Response(status=200)

api.add_resource(Game, '/game')

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')