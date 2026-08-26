
from flask import Flask, render_template, jsonify, request, redirect, url_for

import sys

from app import api_bp
from app.db import db
from app.util import current_user

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')
# 시크릿키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# 블루프린트 등록 관리
app.register_blueprint(api_bp)


def my_groups(user):
    """내가 속한 그룹 목록."""
    return list(db.group.find({"members": user['_id']}, {"_id": 1, "name": 1}))


@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/main')
def render_main():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))
    return render_template('main.html', user=user, groups=my_groups(user), items=[])

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
    return render_template('group/group_create.html')

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
