import enum
import re
from datetime import datetime, timedelta, timezone
from typing import NewType, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class StampType(str, enum.Enum):
    """스탬프 타입"""

    ORDER_DETAILS = "order_details"
    TUMBLER = "tumbler"


class StampBase(BaseModel):
    """Stamp 모델"""

    id: int
    challenge_id: int = Field(
        ..., description="챌린지 ID"
    )  # 후에 다른 챌린지에서 중복 적용 확장성을 위함.
    saved_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="저장 날짜"
    )
    save_url: str
    type: StampType = Field(..., description="스탬프 타입")

    class Config:
        model_config = {"extra": "allow"}


class OrderDetails(StampBase):
    """OrderDetails 스탬프 모델"""

    type: StampType = StampType.ORDER_DETAILS


class Tumbler(StampBase):
    """Tumbler 스탬프 모델"""

    type: StampType = StampType.TUMBLER


class StampInDB(StampBase):
    """Stamp 챌린지 모델"""

    class Config:
        orm_mode = True

    id: int
    challenge_id: int = Field(
        ..., description="챌린지 ID"
    )  # 후에 다른 챌린지에서 중복 적용 확장성을 위함.
    saved_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="저장 날짜"
    )
    save_url: str
    type: StampType = Field(..., description="스탬프 타입")
