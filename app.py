from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request

import sys, os

from app import api_bp

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# 환경변수 세팅 
MONGO_URL = os.environ.get('MONGO_URL')

# DB 서버 세팅
client = MongoClient('MONGO_URL', 27017)
db = client.PeerSolve

# 블루프린트 등록 관리
app.register_blueprint(api_bp)

@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/signup')
def render_signup():
    return render_template('auth/signup.html')

@app.route('/login')
def render_login():
    return render_template('auth/login.html')


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
