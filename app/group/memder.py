from flask import jsonify, request

from . import group_bp
from .group import current_user, parse_group_id
from ..db import db
from ..util import stamp_update


def find_user_by_id(userId):
    if not userId:
        return None
    return db.user.find_one({"ID": userId}, {"_id": 1})


def owned_group(user, group_id):
    return db.group.find_one(
        {"_id": group_id, "owner": user['_id']},
        {"_id": 1, "owner": 1, "members": 1}
    )


def link(group_id, user_id):
    db.group.update_one(
        {"_id": group_id},
        {"$addToSet": {"members": user_id}, "$set": stamp_update()}
    )
    db.user.update_one(
        {"_id": user_id},
        {"$addToSet": {"join_groups": group_id}, "$set": stamp_update()}
    )


def unlink(group_id, user_id):
    db.group.update_one(
        {"_id": group_id},
        {"$pull": {"members": user_id}, "$set": stamp_update()}
    )
    db.user.update_one(
        {"_id": user_id},
        {"$pull": {"join_groups": group_id}, "$set": stamp_update()}
    )


@group_bp.route("/members", methods=['GET'])
def list_members():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    group = db.group.find_one(
        {"_id": group_id, "members": user['_id']},
        {"_id": 1, "owner": 1, "members": 1}
    )
    if group is None:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404

    members = list(db.user.find(
        {"_id": {"$in": group['members']}},
        {"_id": 1, "ID": 1, "nickname": 1}
    ))
    return jsonify([
        {
            "userId": m["ID"],
            "nickname": m.get("nickname"),
            "is_owner": m["_id"] == group["owner"],
        }
        for m in members
    ]), 200


@group_bp.route("/invite", methods=['POST'])
def invite_member():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    group = owned_group(user, group_id)
    if group is None:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404

    target = find_user_by_id((request.form.get('userId') or '').strip())
    if target is None:
        return jsonify({"result": 0, "error": "그런 유저가 없습니다."}), 404

    if target['_id'] in group['members']:
        return jsonify({"result": 0, "error": "이미 그룹 멤버입니다."}), 409

    link(group_id, target['_id'])
    return jsonify({"result": 1}), 201


@group_bp.route("/kick", methods=['DELETE'])
def kick_member():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    group = owned_group(user, group_id)
    if group is None:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404

    target = find_user_by_id((request.args.get('userId') or '').strip())
    if target is None:
        return jsonify({"result": 0, "error": "그런 유저가 없습니다."}), 404

    # owner를 빼면 주인 없는 그룹이 됨. 접으려면 /delete 를 쓰게 한다
    if target['_id'] == group['owner']:
        return jsonify({"result": 0, "error": "그룹장은 추방할 수 없습니다."}), 400

    if target['_id'] not in group['members']:
        return jsonify({"result": 0, "error": "그룹 멤버가 아닙니다."}), 404

    unlink(group_id, target['_id'])
    return jsonify({"result": 1}), 200


@group_bp.route("/leave", methods=['DELETE'])
def leave_group():
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    group = db.group.find_one({"_id": group_id}, {"_id": 1, "owner": 1, "members": 1})
    if group is None or user['_id'] not in group['members']:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404

    if user['_id'] == group['owner']:
        return jsonify({"result": 0, "error": "그룹장은 나갈 수 없습니다. 그룹을 삭제하세요."}), 400

    unlink(group_id, user['_id'])
    return jsonify({"result": 1}), 200
