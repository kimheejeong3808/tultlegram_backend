from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
from bson import ObjectId
from flask import Flask, abort, jsonify, request
from flask_cors import CORS
import jwt
from pymongo import MongoClient


SECRET_KEY = 'turtle'


app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})
client = MongoClient('localhost', 27017)
db = client.turtlegram


def authorize(f):
    @wraps(f)
    def decorated_function():
        if not 'Authorization' in request.headers:
            print("aaaa")
            abort(401)
        token = request.headers['Authorization']
        try:
            print(token)
            user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except:
            print("bbbb")
            abort(401)
        return f(user)

    return decorated_function


@app.route("/")
@authorize
def hello_world(user):
    print(user)
    return jsonify({'message': 'success'})


@app.route("/signup", methods=["POST"])
def sign_up():
    data = json.loads(request.data)
    # data = loads(request.data)
    print(data.get('email'))
    print(data["password"])

    # 이메일 중복시 에러처리

    # 비밀번호 해싱
    pw = data.get('password', None)
    hashed_password = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    doc = {
        'email': data.get('email'),
        'password': hashed_password
    }

    # doc = {
    #     'email': data.get('email'),
    #     'password': data.get('password')
    # }

    print(doc)
    user = db.users.insert_one(doc)
    print(doc)

    return jsonify({"status": "success"})

    # # dump 사용
    # json_doc = dumps(doc)
    # print(json_doc)
    # return json_doc


@app.route("/login", methods=["POST"])
def login():
    print(request)
    data = json.loads(request.data)
    print(data)

    email = data.get("email")
    password = data.get("password")
    hashed_pw = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(hashed_pw)

    result = db.users.find_one({
        'email': email,
        'password': hashed_pw
    })
    print(result)

    if result is None:
        return jsonify({"message": "아이디나 비밀번호가 옳지 않습니다."}), 401

    payload = {
        'id': str(result["_id"]),
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    print(token)

    return jsonify({"message": "success", "token": token})


@app.route("/getuserinfo", methods=["GET"])
@authorize
def get_user_info(user):
    # 제일 위 user만으로도 가능
    # token = request.headers.get("Authorization")

    # if not token:
    #     return jsonify({"message": "no token"}), 402

    # user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    result = db.users.find_one({
        '_id': ObjectId(user["id"])
    })

    return jsonify({"message": "success", "email": result["email"]})


@app.route("/article", methods=["POST"])
@authorize
def post_article(user):
    data = json.loads(request.data)
    print(data)
    print(user)

    db_user = db.users.find_one({'_id': ObjectId(user.get('id'))})
    print(db_user)

    now = datetime.now().strftime("%H:%M:%S")
    doc = {
        'title': data.get('title', None),
        'content': data.get('content', None),
        'user': user['id'],
        'user_email': db_user['email'],
        'time': now,
    }
    print(doc)

    db.article.insert_one(doc)

    return jsonify({"message": "success"})


@app.route("/article", methods=["GET"])
def get_article():
    articles = list(db.article.find())
    print(articles)
    for article in articles:
        print(article.get("title"))
        article["_id"] = str(article["_id"])
    return jsonify({"message": "success", "articles": articles})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
