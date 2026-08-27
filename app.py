
from flask import Flask, render_template, redirect, request, session, url_for
import sys

from app import api_bp, page_bp
from app.util import current_user, group_members, group_of, my_groups, question_items

app = Flask(__name__, static_folder='app/static', template_folder='app/templates')

# 시크릿키 설정
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# 블루프린트 등록 관리
app.register_blueprint(api_bp)
app.register_blueprint(page_bp)

@app.route('/')
def render_index():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))
    return redirect(url_for('render_main'))

@app.route('/main')
def render_main():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))
    groups = my_groups(user)

    # ?group=<id> 면 그 그룹만. 내 그룹 목록에서 직접 골라내므로 남의 그룹 id를
    # 넣어도 안 걸리고, 형식이 깨진 id도 문자열 비교라 예외 안 남
    selected = next(
        (g for g in groups if str(g["_id"]) == request.args.get("group")), None
    )

    # 세션 값으로 대상 그룹을 잡음
    session["selected_group"] = str(selected["_id"]) if selected else None

    items = question_items([selected["_id"]] if selected else [g["_id"] for g in groups])
    return render_template('main.html', user=user, groups=groups, items=items, selected=selected)

# 그룹 관리
@app.route('/groupedit')
def render_group_edit():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))

    group = group_of(user, request.args.get('group'))
    if group is None:
        return redirect(url_for('render_main'))

    tab = 'code' if request.args.get('tab') == 'code' else 'member'
    return render_template(
        'group/group_edit.html',
        user=user,
        group=group,
        tab=tab,
        is_owner=group['owner'] == user['_id'],
        members=group_members(group) if tab == 'member' else [],
        items=question_items([group['_id']]) if tab == 'code' else [],
    )

# 로그인
@app.route('/signup')
def render_signup():
    return render_template('auth/signup.html')

@app.route('/login')
def render_login():
    return render_template('auth/login.html')

@app.route('/upload')
def render_upload():
    user = current_user()
    if user is None:
        return redirect(url_for('render_login'))

    return render_template(
        'question/question_form.html',
        question=None,
        mode="create",
        user=user
    )

if __name__ == '__main__':
    print(sys.executable)
    app.run('0.0.0.0', port=5000, debug=True)
