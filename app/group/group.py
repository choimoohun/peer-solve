'''
  "group": {
    "_id": "ObjectId",
    "name": "String",
    "members": [
      "ObjectId (user_profile._id)"
    ],
    "questions": [
      "ObjectId (question._id)"
    ],
    "owner": "ObjectId (user_profile._id)",
    "at_create": "Timestamp",
    "at_update": "Timestamp"
  },
'''

from flask import jsonify, request, session, redirect, url_for
from pymongo.errors import DuplicateKeyError, PyMongoError

from . import group_bp
from ..db import db
from ..util import stamp_create, stamp_update


def current_user():
    """세션에 로그인된 유저 문서. 없으면 None."""
    userId = session.get('user_login')
    if not userId:
        return None
    return db.user.find_one({"ID": userId}, {"_id": 1})


@group_bp.route("/info", methods=['GET'])
def request_group_list():
    # find()는 Cursor라 jsonify 못 함. list로 풀고 ObjectId는 빼야 직렬화됨
    group_list = list(db.group.find({}, {"_id": 0, "name": 1}))
    return jsonify(group_list), 200


@group_bp.route("/create", methods=['POST'])
def create_group():
    # owner를 폼/쿼리로 받으면 남의 이름으로 그룹 생성 가능. 세션에서만 꺼냄
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_name = (request.form.get('name') or '').strip()
    if not group_name:
        return jsonify({"result": 0, "error": "그룹 이름을 입력하세요."}), 400

    info = {
        "name": group_name,
        "members": [user['_id']],
        "questions": [],
        "owner": user['_id'],
        **stamp_create()
    }

    try:
        result = db.group.insert_one(info)
    except DuplicateKeyError:
        return jsonify({"result": 0, "error": "이미 존재하는 그룹입니다."}), 409
    except PyMongoError as e:
        return jsonify({"result": 0, "error": f"데이터베이스 오류가 발생했습니다: {str(e)}"}), 500

    db.user.update_one(
        {"_id": user['_id']},
        {"$addToSet": {"join_groups": result.inserted_id},
        "$set": stamp_update()}
    )

    return jsonify({
        "result": 1,
        "group_id": str(result.inserted_id),
        "redirect": url_for('render_main')
    }), 201


@group_bp.route("/delete", methods=['DELETE'])
def delete_group():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_name = request.args.get('group')

    # owner는 스키마상 ObjectId. 쿼리로 받은 문자열로 찾으면 절대 안 걸림
    result = db.group.delete_one({
        'owner': user['_id'],
        'name': group_name
    })

    if result.deleted_count == 1:
        return jsonify({"result": 1}), 200
    return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404


@group_bp.route("/edit", methods=['PUT'])
def edit_group_name():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_name = request.args.get('group')
    change_name = (request.args.get('change') or '').strip()
    if not change_name:
        return jsonify({"result": 0, "error": "바꿀 이름을 입력하세요."}), 400

    result = db.group.update_one(
        {'owner': user['_id'], 'name': group_name},
        {'$set': {'name': change_name, **stamp_update()}}
    )

    if result.matched_count == 0:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404
    return jsonify({"result": 1, "name": change_name}), 200
