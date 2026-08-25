from pymongo import MongoClient
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import os

# 환경변수 세팅
load_dotenv()
MONGO_URL = os.environ.get('MONGO_URL')

# DB 서버 세팅
# Mongo는 UTC로 저장. 읽을 때 KST로 돌려받게 설정 (안 하면 naive UTC)
client = MongoClient(MONGO_URL, tz_aware=True, tzinfo=ZoneInfo("Asia/Seoul"))
db = client.PeerSolve

# 동시 가입 경합 방지 (앱단 중복 체크만으로는 못 막음)
db.user.create_index("ID", unique=True)
db.user.create_index("nickname", unique=True)

# 같은 사람이 같은 이름 그룹 두 번 못 만들게. 앱단 체크는 동시 요청에 뚫림
db.group.create_index([("owner", 1), ("name", 1)], unique=True)
