import enum
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, NewType, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ChallengeBase(BaseModel):
    """ChallengeBase 기본 정보 모델"""

    id: int
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    started_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="시작 날짜"
    )
    due_at: datetime = Field(
        default_factory=datetime.date(datetime.now(timezone.utc) + timedelta(days=14)),
        description="종료 날짜",
    )

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class ChallengeCreate(ChallengeBase):
    """Challenge 챌린지 생성 모델"""

    stamp_ids: List[int] = []


class ChallengeResponse(ChallengeBase):
    """Challenge 챌린지 응답 모델"""

    stamps: List[Any]  # stamps


class ChallengeInDB(ChallengeBase):
    """Challenge 챌린지 모델"""

    class Config:
        orm_mode = True
