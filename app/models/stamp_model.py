import enum
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, NewType, Optional, Union

from pydantic import BaseModel, EmailStr, Field, field_validator


class StampType(str, enum.Enum):
    """스탬프 타입"""

    ORDER_DETAILS = "order_details"
    TUMBLER = "tumbler"


class StampBase(BaseModel):
    """Stamp 모델"""

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


class StampCreate(StampBase):
    """Stamp 챌린지 생성 모델"""

    challenge_ids: List[int] = []  # 후에 다른 챌린지에서 중복 적용 확장성을 위함.


class StampResponse(BaseModel):
    """Stamp 챌린지 응답 모델"""

    id: int
    saved_at: Union[str, datetime] = Field(
        ..., description="저장 날짜 (YYYY-MM-DD) 문자열"
    )
    save_url: str
    type: StampType = Field(..., description="스탬프 타입")

    @classmethod
    def timestamp_to_datestr(
        cls,
        id: int,
        saved_at: Union[str, datetime],
        save_url: str,
        type: StampType,
    ) -> "StampResponse":
        """타임스탬프를 날짜 문자열로 변환하는 메서드"""
        if isinstance(saved_at, datetime):
            saved_at_str = saved_at.strftime("%Y-%m-%d")
        elif isinstance(saved_at, str):
            saved_at_str = saved_at

        return cls(
            id=id,
            saved_at=saved_at_str,
            save_url=save_url,
            type=type,
        )


class StampInDB(StampBase):
    """Stamp 챌린지 모델"""

    class Config:
        orm_mode = True

    id: int
    saved_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), description="저장 날짜"
    )
    save_url: str
    type: StampType = Field(..., description="스탬프 타입")
