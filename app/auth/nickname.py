import random

ADJECTIVES = [
    "졸린", "배고픈", "성실한", "느긋한", "재빠른", "용감한", "엉뚱한", "차분한",
    "수줍은", "명랑한", "똑똑한", "게으른", "따뜻한", "시원한", "달콤한", "매콤한",
]

NOUNS = [
    "고양이", "강아지", "너구리", "다람쥐", "펭귄", "부엉이", "고슴도치", "수달",
    "판다", "여우", "토끼", "개구리", "돌고래", "코알라", "미어캣", "알파카",
]


def random_nickname():
    return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randrange(1000, 10000)}"
