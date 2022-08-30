from flask import Flask, Response
from game import careersGame

app = Flask(__name__)

@app.route('/')
def default():
    return Response(status=200)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')