from flask import jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from zoneinfo import ZoneInfo

from . import auth_bp
from .nickname import random_nickname
from db import db

KST = ZoneInfo("Asia/Seoul")

@auth_bp.route("/login", methods=['POST'])
def login():
    userId = request.form.get('userId')
    password = request.form.get('userPassword')

    user = db.user.find_one({"ID": userId}, {"ID": 1, "password": 1, "_id": 0})
    if user is None or not check_password_hash(user['password'], password):

        return jsonify({"result": "failure"}), 401

    session['user_login'] = userId
    return redirect(url_for('render_index'))


@auth_bp.route("/signup", methods=['POST'])
def signup():
    userId = request.form.get('userId')
    password = request.form.get('userPassword')
    confirmPassword = request.form.get('userConfirmPassword')

    if not userId or not password:
        return jsonify({"result": "failure", "reason": "empty"}), 400

    if password != confirmPassword:
        return jsonify({"result": "failure", "reason": "password_mismatch"}), 400

    if db.user.find_one({"ID": userId}, {"_id": 1}):
        return jsonify({"result": "failure", "reason": "duplicate_id"}), 409

    now = datetime.now(KST)

    nickname = random_nickname()
    while db.user.find_one({"nickname": nickname}, {"_id": 1}):
        nickname = random_nickname()

    try:
        db.user.insert_one({
            "ID": userId,
            "password": generate_password_hash(password),
            "nickname": nickname,
            "join_groups": [],
            "at_create": now,
            "at_update": now
        })
    except DuplicateKeyError:
        return jsonify({"result": "failure", "reason": "duplicate_id"}), 409

    return redirect(url_for('render_index'))


@auth_bp.route("/logout")
def logout():
    session.pop('user_login', None)
    return redirect(url_for('render_index'))
