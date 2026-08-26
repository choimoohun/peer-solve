from bson import ObjectId
from flask import request, jsonify, session, render_template

from . import question_api_bp
from ..db import db
from ..util import stamp_create, stamp_update


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


@question_api_bp.route("/", methods=["POST"])
def upload_question():
    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    group = current_group()
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
        return jsonify({"result": "failure", "message": "타이틀이 비어있습니다."}), 400

    if not language:
        return (
            jsonify({"result": "failure", "message": "언어가 선택되지 않았습니다."}),
            400,
        )

    if not code:
        return jsonify({"result": "failure", "message": "코드가 비어있습니다."}), 400

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


@question_api_bp.route("/list", methods=["GET"])
def get_questions():
    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    group = current_group()
    if not group:
        return jsonify({"result": "failure", "message": "선택된 그룹이 없습니다."}), 400

    if user["_id"] not in group["members"]:
        return (
            jsonify({"result": "failure", "message": "해당 그룹의 멤버가 아닙니다."}),
            403,
        )

    questions = list(db.question.find({"_id": {"$in": group["questions"]}}))

    if not questions:
        return jsonify({"result": "success", "questions": []}), 200

    for question in questions:
        question["_id"] = str(question["_id"])
        question["owner"] = str(question["owner"])
        question["group_id"] = str(question["group_id"])

    return jsonify({"result": "success", "questions": questions}), 200


@question_api_bp.route("/<question_id>", methods=["PATCH"])
def update_question(question_id):
    question = db.question.find_one({"_id": ObjectId(question_id)})
    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾을 수 없습니다."}), 404

    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401
    if question["owner"] != user["_id"]:
        return jsonify({"result": "failure", "message": "작성자가 아닙니다."}), 403

    group = db.group.find_one({"_id": question["group_id"]})
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
        return jsonify({"result": "failure", "message": "타이틀이 비어있습니다."}), 400

    if not language:
        return (
            jsonify({"result": "failure", "message": "언어가 선택되지 않았습니다."}),
            400,
        )

    if not code:
        return jsonify({"result": "failure", "message": "코드가 비어있습니다."}), 400

    data = {
        "title": title,
        "language": language,
        "code": code,
        **stamp_update(),
    }

    db.question.update_one({"_id": question["_id"]}, {"$set": data})

    return jsonify({"result": "success", "question_id": question_id}), 200


@question_api_bp.route("/<question_id>", methods=["DELETE"])
def delete_question(question_id):
    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    question = db.question.find_one({"_id": ObjectId(question_id)})
    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾을 수 없습니다."}), 404

    if question["owner"] != user["_id"]:
        return jsonify({"result": "failure", "message": "작성자만 코드를 삭제할 수 있습니다."}), 403

    group = db.group.find_one({"_id": question["group_id"]})
    if not group:
        return jsonify({"result": "failure", "message": "그룹이 없습니다."}), 400

    if user["_id"] not in group["members"]:
        return (
            jsonify({"result": "failure", "message": "해당 그룹의 멤버가 아닙니다."}),
            403,
        )

    db.comment.delete_many({"question_id": question["_id"]})

    db.group.update_one(
        {"_id": group["_id"]},
        {"$pull": {"questions": question["_id"]}},
    )

    db.question.delete_one({"_id": question["_id"]})

    return jsonify({"result": "success"}), 200
