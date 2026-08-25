# 환경변수 세팅 
MONGO_URL = os.environ.get('MONGO_URL')

# DB 서버 세팅
client = MongoClient('MONGO_URL', 27017)
db = client.PeerSolve
