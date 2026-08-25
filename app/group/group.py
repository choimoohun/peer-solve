'''
  "group": {
    "_id": "ObjectId",
    "name": "String",
    "members": [
      "ObjectId (user_profile._id)"
    ],
    "owner": "ObjectId (user_profile._id)",
    "at_create": "Timestamp",
    "at_update": "Timestamp"
  },
'''

from bson import ObjectId
from bson.errors import InvalidId
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


def parse_group_id():
    """쿼리스트링 id를 ObjectId로 바꿈. 형식 틀리면 None (24자리 hex 아니면 예외 남)."""
    try:
        return ObjectId(request.args.get('id'))
    except (InvalidId, TypeError):
        return None


@group_bp.route("/info", methods=['GET'])
def request_group_list():
    """내가 속한 그룹 목록. [{id, name, is_owner}] 형태.
    """
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_list = [
        {
            "id": str(g["_id"]),
            "name": g["name"],
            "is_owner": g["owner"] == user['_id'],
        }
        for g in db.group.find(
            {"members": user['_id']},
            {"_id": 1, "name": 1, "owner": 1}
        )
    ]
    return jsonify(group_list), 200


@group_bp.route("/create", methods=['POST'])
def create_group():
    """그룹 만들고 생성자를 owner 겸 첫 멤버로 넣음.

    form: name
    """
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_name = (request.form.get('name') or '').strip()
    if not group_name:
        return jsonify({"result": 0, "error": "그룹 이름을 입력하세요."}), 400

    info = {
        "name": group_name,
        "members": [user['_id']],
        "owner": user['_id'],
        **stamp_create()
    }

    # 좀 예쁘게 주지
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
    """본인이 owner인 그룹 지움. query: id
    """
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    result = db.group.delete_one({
        '_id': group_id,
        'owner': user['_id']
    })

    if result.deleted_count == 1:
        # 멤버들 join_groups에 남은 id 청소. 안 하면 없는 그룹을 가리키는 쓰레기가 쌓임
        db.user.update_many(
            {"join_groups": group_id},
            {"$pull": {"join_groups": group_id}, "$set": stamp_update()}
        )
        return jsonify({"result": 1}), 200
    return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404


@group_bp.route("/edit", methods=['PUT'])
def edit_group_name():
    """그룹 이름 변경. query: id, change
    """
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    change_name = (request.args.get('change') or '').strip()
    if not change_name:
        return jsonify({"result": 0, "error": "바꿀 이름을 입력하세요."}), 400

    result = db.group.update_one(
        {'_id': group_id, 'owner': user['_id']},
        {'$set': {'name': change_name, **stamp_update()}}
    )

    if result.matched_count == 0:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404
    return jsonify({"result": 1, "name": change_name}), 200
