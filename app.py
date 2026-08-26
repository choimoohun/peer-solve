
from flask import Flask, render_template, redirect, url_for

import sys

from app import api_bp, page_bp
from app.util import current_user, my_groups, question_items

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')
# 시크릿키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# 블루프린트 등록 관리
app.register_blueprint(api_bp)
app.register_blueprint(page_bp)

@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/main')
def render_main():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))
    groups = my_groups(user)
    items = question_items(g["_id"] for g in groups)
    return render_template('main.html', user=user, groups=groups, items=items)

# 로그인
@app.route('/signup')
def render_signup():
    return render_template('auth/signup.html')

@app.route('/login')
def render_login():
    return render_template('auth/login.html')

@app.route('/upload')
def render_upload():
    return render_template('question/question_form.html',
                           question=None,
                           mode="create")

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
