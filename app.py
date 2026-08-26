
from flask import Flask, render_template, jsonify, request

import sys

from app import api_bp

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')
# 시크릿키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# 블루프린트 등록 관리
app.register_blueprint(api_bp)

@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/main')
def render_main():
    return render_template('main.html')

# 로그인
@app.route('/signup')
def render_signup():
    return render_template('auth/signup.html')

@app.route('/login')
def render_login():
    return render_template('auth/login.html')

# 그룹
@app.route('/groupedit')
def render_group_edit():
    return render_template('group/gorup_edit.html')

@app.route('/groupcreate')
def render_group_create():
    return render_template('auth/group_create.html')

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
