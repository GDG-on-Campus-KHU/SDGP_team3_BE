FAKE_USERS = {
    1: {"id": 1, "email": "test1@example.com", "username": "테스트유저1"},
    2: {"id": 2, "email": "test2@example.com", "username": "테스트유저2"},
}

FAKE_CHALLENGES = {
    1: [
        {"id": 1, "title": "텀블러 사용하기", "completed": True},
        {"id": 2, "title": "일회용 컵 줄이기", "completed": False},
    ],
    2: [{"id": 3, "title": "플라스틱 빨대 안쓰기", "completed": True}],
}

FAKE_DECORATIONS = {
    1: [
        {"id": 1, "type": "배지", "name": "친환경 입문자"},
        {"id": 2, "type": "배지", "name": "챌린지 마스터"},
    ],
    2: [{"id": 3, "type": "아이콘", "name": "에코 워리어"}],
}

from datetime import datetime

from app.models.user_model import User


def get_fake_user_info(user_info: dict) -> User:
    return User(
        id=1,
        email=user_info["email"],
        username=user_info.get("name", "google_user"),
        is_active=True,
        created_at=datetime.utcnow(),
    )
