from pymongo import MongoClient
from flask import Flask

import sys, os

from app import api_bp

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# 환경변수 세팅 
MONGODB_URL = os.environ.get('MONGODB_URL')

# DB 서버 세팅
client = MongoClient('MONGODB_URL', 27017)
db = client.PeerSolve

# 블루프린트 등록 관리
app.register_blueprint(api_bp)

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
