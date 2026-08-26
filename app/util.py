from datetime import datetime
from zoneinfo import ZoneInfo

from flask import session

from .db import db

KST = ZoneInfo("Asia/Seoul")


def now():
    """현재 KST 시각. at_create / at_update 박을 때 씀."""
    return datetime.now(KST)


def stamp_create():
    """새 문서 삽입용. at_create / at_update 동일 값으로 세팅함."""
    t = now()
    return {"at_create": t, "at_update": t}


def stamp_update():
    """수정용. $set에 펼쳐 씀."""
    return {"at_update": now()}


def current_user():
    """세션에 로그인된 유저 문서. 없으면 None."""
    userId = session.get('user_login')
    if not userId:
        return None
    return db.user.find_one({"ID": userId}, {"_id": 1, "ID": 1, "nickname": 1})


def my_groups(user):
    """내가 속한 그룹 목록. group.members 인덱스 태움."""
    return list(db.group.find({"members": user['_id']}, {"_id": 1, "name": 1}))


def nickname_of(user_ids):
    """user._id -> nickname 맵.

    owner / members 는 ObjectId라 그대로 뿌리면 화면에 id가 찍힘.
    한 번의 $in 조회로 끝냄. 건마다 find_one 하면 N+1 쿼리가 됨.
    """
    return {u["_id"]: u["nickname"]
            for u in db.user.find({"_id": {"$in": list(user_ids)}}, {"nickname": 1})}


def question_items(group_ids, limit=20):
    """그룹들의 질문을 템플릿용 dict로. 최신순.

    (group_id, at_create) 복합 인덱스에 맞춘 조회. owner는 닉네임으로,
    at_create는 표시용 문자열로 바꿔서 넘김.
    """
    questions = list(
        db.question.find({"group_id": {"$in": list(group_ids)}})
        .sort("at_create", -1).limit(limit)
    )
    nick = nickname_of({q["owner"] for q in questions})
    return [
        {
            "title": q.get("title", "(제목 없음)"),
            "owner": nick.get(q["owner"], "알 수 없음"),
            "at_create": q["at_create"].strftime("%Y-%m-%d"),
        }
        for q in questions
    ]
