from bson import ObjectId
from flask import request, jsonify, session

from . import comment_bp
from .question_api import current_user, current_group
from ..db import db
from ..util import stamp_create


def find_question(question_id):
    try:
        return db.question.find_one({
            "_id": ObjectId(question_id)
        })
    except Exception:
        return None


@comment_bp.route("/add", methods=["POST"])
def add_comment():
    # TODO: 댓글 작성 구현
    return
