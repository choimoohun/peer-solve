"""그룹 멤버 관리. 초대 / 추방 / 나가기 / 목록.

group.members 와 user_profile.join_groups 는 같은 관계를 양쪽에서 들고 있음.
한쪽만 고치면 바로 어긋나므로 관계 변경은 반드시 link() / unlink()로만 함.
"""

from flask import jsonify, request

from . import group_bp
from .group import current_user, parse_group_id
from ..db import db
from ..util import stamp_update


def find_user_by_id(userId):
    """로그인 ID로 유저 문서 찾음. 없거나 빈 값이면 None."""
    if not userId:
        return None
    return db.user.find_one({"ID": userId}, {"_id": 1})


def owned_group(user, group_id):
    """본인이 owner인 그룹만 돌려줌. 아니면 None.
    """
    return db.group.find_one(
        {"_id": group_id, "owner": user['_id']},
        {"_id": 1, "owner": 1, "members": 1}
    )


def link(group_id, user_id):
    """멤버 링크. group.members와 user.join_groups 양쪽 모두.
    """
    db.group.update_one(
        {"_id": group_id},
        {"$addToSet": {"members": user_id}, "$set": stamp_update()}
    )

    db.user.update_one(
        {"_id": user_id},
        {"$addToSet": {"join_groups": group_id}, "$set": stamp_update()}
    )


def unlink(group_id, user_id):
    """멤버 링크 해제.

    추방/나가기/그룹삭제가 전부 이 함수 거쳐야 두 컬렉션이 안 어긋남.
    """
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
    """그룹 멤버 목록. query: id
    """
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
    """승인 절차 없이 owner가 유저를 그룹에 넣음. query: id / form: userId
    """
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
    """추방 기능. query: id, userId
    """
    user = current_user()
    if user is None:
        return jsonify({"result": 0, "error": "로그인이 필요합니능다."}), 401

    group_id = parse_group_id()
    if group_id is None:
        return jsonify({"result": 0, "error": "그룹 id가 올바르지 않습니다."}), 400

    group = owned_group(user, group_id)
    if group is None:
        return jsonify({"result": 0, "error": "그룹을 찾을 수 없습니다."}), 404

    target = find_user_by_id((request.args.get('userId') or '').strip())
    if target is None:
        return jsonify({"result": 0, "error": "그런 유저가 없습니다."}), 404

    # owner를 빼면 주인 없는 그룹이 됨. 접으려면 /delete 를 쓰게 함
    if target['_id'] == group['owner']:
        return jsonify({"result": 0, "error": "그룹장은 추방할 수 없습니다."}), 400

    if target['_id'] not in group['members']:
        return jsonify({"result": 0, "error": "그룹 멤버가 아닙니다."}), 404

    unlink(group_id, target['_id'])
    return jsonify({"result": 1}), 200


@group_bp.route("/leave", methods=['DELETE'])
def leave_group():
    """멤버가 스스로 나가기. query: id
    """
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
