from pymongo import MongoClient
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import os

# 환경변수 세팅
load_dotenv()
MONGO_URL = os.environ.get('MONGO_URL')

# DB 서버 세팅
# Mongo는 UTC로 저장함. 읽을 때 KST로 돌려받게 설정
client = MongoClient(MONGO_URL, tz_aware=True, tzinfo=ZoneInfo("Asia/Seoul"))
db = client.PeerSolve

# 동시 가입 경합 방지 
db.user.create_index("ID", unique=True)
db.user.create_index("nickname", unique=True)

# 같은 사람이 같은 이름 그룹 두 번 못 만들게 막음. 앱단 체크는 동시 요청에 뚫림
db.group.create_index([("owner", 1), ("name", 1)], unique=True)

# 역참조 조회용. group.questions 배열을 안 두는 대신 여기로 찾음
db.group.create_index("members")
db.question.create_index([("group_id", 1), ("at_create", -1)])
db.comment.create_index([("question_id", 1), ("at_create", 1)])
