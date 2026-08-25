from pymongo import MongoClient
from flask import Flask

import sys

from app import api_bp

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# DB 서버 세팅
client = MongoClient('localhost', 27017)
db = client.dbjungle

# 블루프린트 등록 관리
app.register_blueprint(api_bp)

@app.route('/')
def hello_world():
    return 'Hello, World!'


if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
