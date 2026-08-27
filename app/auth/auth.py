from flask import jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from . import auth_bp
from .nickname import random_nickname
from ..group.group import insert_group
from ..db import db
from ..util import stamp_create

@auth_bp.route("/login", methods=['POST'])
def login():
    """로그인.

    비밀번호는 해시로만 저장돼 있어서 check_password_hash로 대조
    """
    userId = request.form.get('userId')
    password = request.form.get('userPassword')

    user = db.user.find_one({"ID": userId}, {"ID": 1, "password": 1, "_id": 0})
    if user is None or not check_password_hash(user['password'], password):

        return redirect(url_for('render_login', error=1))

    session['user_login'] = userId
    return redirect(url_for('render_main'))


@auth_bp.route("/signup", methods=['POST'])
def signup():
    """회원가입. 닉네임은 랜덤
    """
    userId = request.form.get('userId')
    password = request.form.get('userPassword')
    confirmPassword = request.form.get('userConfirmPassword')

    if not userId or not password:
        return jsonify({"result": "failure", "reason": "empty"}), 400

    if password != confirmPassword:
        return jsonify({"result": "failure", "reason": "password_mismatch"}), 400

    if db.user.find_one({"ID": userId}, {"_id": 1}):
        return jsonify({"result": "failure", "reason": "duplicate_id"}), 409

    nickname = random_nickname()
    while db.user.find_one({"nickname": nickname}, {"_id": 1}):
        nickname = random_nickname()

    try:
        result = db.user.insert_one({
            "ID": userId,
            "password": generate_password_hash(password),
            "nickname": nickname,
            **stamp_create()
        })
    except DuplicateKeyError:
        return jsonify({"result": "failure", "reason": "duplicate_id"}), 409

    # 가입하면 본인이 owner인 개인 그룹 하나 자동 생성
    insert_group(result.inserted_id, f"{nickname}의 그룹")

    return redirect(url_for('render_login'))


@auth_bp.route("/logout")
def logout():
    """로그아웃"""
    session.pop('user_login', None)
    return redirect(url_for('render_main'))
