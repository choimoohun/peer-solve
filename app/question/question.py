from bson import ObjectId
from flask import request, jsonify, session

from . import question_bp
from ..db import db
from ..util import stamp_create


def current_user():
    user_id = session.get("user_login")
    if not user_id:
        return None
    return db.user.find_one({"ID": user_id}, {"_id": 1})


def current_group():
    group_id = session.get("selected_group")
    if not group_id:
        return None
    return db.group.find_one({"_id": ObjectId(group_id)})


@question_bp.route("/", methods=["POST"])
def upload_question():
    user = current_user()
    group = current_group()

    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    if not group:
        return jsonify({"result": "failure", "message": "선택된 그룹이 없습니다."}), 400

    if user["_id"] not in group["members"]:
        return (
            jsonify({"result": "failure", "message": "해당 그룹의 멤버가 아닙니다."}),
            403,
        )

    title = request.form.get("title")
    language = request.form.get("language")
    code = request.form.get("code")

    if not title:
        return jsonify({"result": "failure", "message": "타이틀이 비어있습니다"}), 400

    if not language:
        return (
            jsonify({"result": "failure", "message": "언어가 선택되지 않았습니다"}),
            400,
        )

    if not code:
        return jsonify({"result": "failure", "message": "코드가 비어있습니다"}), 400

    data = {
        "owner": user["_id"],
        "group_id": group["_id"],
        "title": title,
        "language": language,
        "code": code,
        **stamp_create(),
    }

    result = db.question.insert_one(data)

    db.group.update_one(
        {"_id": group["_id"]}, {"$push": {"questions": result.inserted_id}}
    )

    return jsonify({"result": "success", "question_id": str(result.inserted_id)}), 201
