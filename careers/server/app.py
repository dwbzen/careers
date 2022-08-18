from flask import Flask, render_template, send_from_directory, Response
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/ping')
def ping():
    return Response(status=200)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')