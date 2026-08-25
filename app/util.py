from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")


def now():
    """현재 KST 시각. at_create / at_update 박을 때 사용."""
    return datetime.now(KST)


def stamp_create():
    """새 문서 삽입용. at_create / at_update 동일 값으로 세팅."""
    t = now()
    return {"at_create": t, "at_update": t}


def stamp_update():
    """수정용. $set에 펼쳐 쓰기."""
    return {"at_update": now()}
