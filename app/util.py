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
