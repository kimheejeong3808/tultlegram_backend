import hashlib
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.turtlegram


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


@app.route("/")
def hello_world():
    return jsonify({'message': 'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)

    email = data['email']
    password = data['password']

    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {'email': email, 'password': hashed_password}
    db.users.insert_one(doc)

    return jsonify({'message': 'success2'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
