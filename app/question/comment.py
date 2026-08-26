from bson import ObjectId
from flask import request, jsonify

from . import comment_bp
from .question_api import current_user, current_group
from ..db import db
from ..util import stamp_create, nickname_of


def find_question(question_id):
    try:
        return db.question.find_one({"_id": ObjectId(question_id)})
    except Exception:
        return None


@comment_bp.route("/<question_id>", methods=["GET"])
def get_comments(question_id):
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

    question = find_question(question_id)
    if not question:
        return jsonify({"result": "failure", "message": "존재하지 않는 코드입니다."}), 404


    comments = list(db.comment.find({"question_id": question["_id"]}).sort("at_create", -1))

    nick = nickname_of({c["owner"] for c in comments})

    for comment in comments:
        comment["nickname"] = nick.get(comment["owner"], "알 수 없음")

        comment["_id"] = str(comment["_id"])
        comment["owner"] = str(comment["owner"])
        comment["question_id"] = str(comment["question_id"])

    return jsonify({"result": "success", "count": len(comments), "comments": comments})


@comment_bp.route("/<question_id>", methods=["POST"])
def add_comment(question_id):
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

    question = find_question(question_id)
    if not question:
        return jsonify({"result": "failure", "message": "존재하지 않는 코드입니다."}), 404

    text = request.form.get("text", "").strip()
    if not text:
        return jsonify({"result": "failure", "message": "댓글 내용을 입력해주세요."}), 400

    data = {
        "text": text,
        "owner": user["_id"],
        "question_id": question["_id"],
        **stamp_create()
    }

    result = db.comment.insert_one(data)

    return jsonify({"result": "success", "comment_id": str(result.inserted_id)}), 201
