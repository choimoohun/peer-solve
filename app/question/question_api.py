from bson import ObjectId
from flask import request, jsonify, session, render_template

from . import question_api_bp
from ..db import db
from ..util import stamp_create, stamp_update


# group.questions 배열을 걷어냄. 질문-그룹 관계는 question.group_id
# 하나만 정본으로 씀. 이유는 각 함수 주석 참고. 되돌리려면 group 문서에 배열을
# 다시 두고 upload/delete 양쪽에서 $push/$pull 을 살려야 함.

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

    # 예전엔 여기서 group 문서에 $push {questions: 새 id} 도 했음. 지웠음.
    # group_id 가 data 에 이미 들어있어서 같은 사실을 두 번 적는 꼴이었고,
    # 두 컬렉션을 잇는 write 라 중간에 끊기면 한쪽만 반영되는 문제가 있었음.
    result = db.question.insert_one(data)

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

    # 예전엔 {"_id": {"$in": group["questions"]}} 로 찾았음. 그런데 insert_group()
    # 이 questions 키를 안 만들어서, 질문이 0개인 새 그룹에서 KeyError 500 이 났음.
    # 이제 group 문서를 안 보고 question 쪽에서 역으로 찾음.
    # db.py 의 (group_id, at_create 내림차순) 복합 인덱스를 그대로 태움.
    # 부수 효과로 정렬이 삽입순 -> 최신순으로 바뀜.
    questions = list(
        db.question.find({"group_id": group["_id"]}).sort("at_create", -1)
    )

    # 빈 리스트일 때 조기 반환하던 분기도 지웠음. 아래 for 문이 그냥 통과하고
    # 똑같은 응답이 나가서 필요 없었음.

    for question in questions:
        question["_id"] = str(question["_id"])
        question["owner"] = str(question["owner"])
        question["group_id"] = str(question["group_id"])

    return jsonify({"result": "success", "questions": questions}), 200


@question_api_bp.route("/<question_id>", methods=["GET"])
def get_question(question_id):
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

    # 원래 find_one({}, {"_id": ..., "group_id": ...}) 이었음. 조건이 두 번째 인자
    # (projection) 자리에 들어가 있어서 필터가 사실상 {} 였고, 컬렉션에서 아무 문서나
    # 1개가 리턴됐음. group_id 도 안 걸려서 다른 그룹 질문까지 열렸음.
    # 인자 하나로 합쳐서 필터로 넘김.
    question = db.question.find_one({"_id": ObjectId(question_id), "group_id": group["_id"]})

    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾지 못했습니다."}), 404

    question["_id"] = str(question["_id"])
    question["owner"] = str(question["owner"])
    question["group_id"] = str(question["group_id"])

    return jsonify({"result": "success", "question": question})


@question_api_bp.route("/<question_id>", methods=["PUT"])
def update_question(question_id):
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

    question = db.question.find_one({"_id": ObjectId(question_id), "group_id": group["_id"]})
    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾을 수 없습니다."}), 404

    if question["owner"] != user["_id"]:
        return jsonify({"result": "failure", "message": "작성자가 아닙니다."}), 403

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

    group = current_group()
    if not group:
        return jsonify({"result": "failure", "message": "그룹이 없습니다."}), 400

    if user["_id"] not in group["members"]:
        return (
            jsonify({"result": "failure", "message": "해당 그룹의 멤버가 아닙니다."}),
            403,
        )

    question = db.question.find_one({"_id": ObjectId(question_id), "group_id": group["_id"]})
    if not question:
        return jsonify({"result": "failure", "message": "코드를 찾을 수 없습니다."}), 404

    if question["owner"] != user["_id"]:
        return jsonify({"result": "failure", "message": "작성자만 코드를 삭제할 수 있습니다."}), 403

    db.group.update_one(
        {"_id": group["_id"]},
        {"$pull": {"questions": question["_id"]}},
    )

    db.question.delete_one({"_id": question["_id"]})

    return jsonify({"result": "success"}), 200
