from flask import request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo

from . import question_bp
from db import db


def is_auth(user_id, group_id):
    # TODO: 실제 그룹원 확인
    return True


KST = ZoneInfo("Asia/Seoul")


@question_bp.route("/", methods=["POST"])
def upload_question():
    user_id = "user1" # 임시 값
    group_id = "group1" # 임시 값

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

    if not is_auth(user_id, group_id):
        return jsonify({"result": "failure", "message": "업로드 권한이 없습니다"}), 403

    now = datetime.now(KST)

    data = {
        "owner": user_id,
        "group_id": group_id,
        "title": title,
        "language": language,
        "code": code,
        "at_create": now,
        "at_update": now,
    }

    db.questions.insert_one(data)

    return jsonify({"result": "success"}), 201
