import enum
import re
from datetime import datetime, timedelta, timezone
from typing import NewType, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class ChallengeBase(BaseModel):
    """ChallengeBase 기본 정보 모델"""

    id: int
    stamp_id: int = Field(
        ..., description="스탬프 ID"
    )  # 후에 다른 챌린지에서 중복 적용 확장성을 위함.
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    started_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="시작 날짜"
    )
    due_at: datetime = Field(
        default_factory=datetime.date(datetime.now(timezone.utc) + timedelta(days=14)),
        description="종료 날짜",
    )
    version: str = Field(..., max_length=10, description="챌린지 버전")

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class Challenge(ChallengeBase):
    """Challenge 챌린지 모델"""

    pass


class ChallengeInDB(ChallengeBase):
    """Challenge 챌린지 모델"""

    class Config:
        orm_mode = True
