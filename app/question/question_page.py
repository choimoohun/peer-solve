from bson import ObjectId
from flask import jsonify, render_template

from . import question_page_bp
from .question_api import current_user
from ..db import db


@question_page_bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    groups = db.group.find({"members": user["_id"]}, {"_id": 1})
    if not groups:
        return jsonify({"result": "failure", "message": "가입된 그룹이 없습니다."}), 400

    group_ids = [group["_id"] for group in groups]
    question = db.question.find_one({"_id": ObjectId(question_id), "group_id": {"$in": group_ids}})

    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾지 못했습니다."}), 404

    owner = db.user.find_one({"_id": question["owner"]})
    is_owner = question["owner"] == user["_id"]

    return render_template(
        "question/question.html",
        question=question,
        owner=owner,
        is_owner=is_owner
    )


@question_page_bp.route("/<question_id>/edit", methods=["GET"])
def edit_question(question_id):
    user = current_user()
    if not user:
        return jsonify({"result": "failure", "message": "로그인이 필요합니다."}), 401

    question = db.question.find_one({"_id": ObjectId(question_id)})
    if not question:
        return jsonify({"result": "failure", "message": "존재하지 않는 코드입니다."}), 404

    if question["owner"] != user["_id"]:
        return jsonify({"result": "failure", "message": "수정 권한이 필요합니다."}), 403

    return render_template(
        "question/question_form.html",
        question=question,
        mode="edit"
    )
