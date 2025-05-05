# decoration_user_model.py
import enum
import json
import re
from datetime import datetime, timezone
from typing import Any, List, NewType, Optional, Union

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.decoration_model import (
    AssetType,
    DecorationBase,
    DecorationInDB,
    DecorationType,
    LandscapeType,
)


class DecorationUserBase(BaseModel):
    """DecorationBase 기본 정보 모델"""

    did: int = Field(..., description="장식 ID")
    uid: int = Field(..., description="사용자 ID")
    acquired_at: datetime = Field(
        ..., description="장식 획득 시간 (ISO 8601 포맷)"
    )  # 지원: YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]
    is_equipped: bool = Field(..., description="장식 장착 여부")
    type: DecorationType = Field(..., description="장식 타입")

    class Config:
        model_config = {"extra": "allow"}


class CreateDecorationUser(DecorationUserBase):
    """
    사용자의 Decoration 얻을 때 모델
    - uid: 사용자 ID
    - did: 장식 ID
    - acquired_at: 장식 획득 시간 (ISO 8601 포맷)
    - is_equipped: 장식 장착 여부 (일단 False로 설정)
    - type: 장식 타입
    """

    @field_validator("acquired_at")
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("타임존 정보가 필요합니다.")
        return v


class DecorationUserInDB(BaseModel):
    """decoration_user 데이터베이스 모델"""

    # from_orm 사용
    class Config:
        orm_mode = True  # from_orm 메서드 활성화 및 ORM

    did: int
    uid: int
    acquired_at: datetime
    is_equipped: bool
    type: DecorationType


# 합성(Composition)을 위한 모델 (Has-A 관계)
class DecorationUserWithDetails(BaseModel):
    # DecorationUser의 필드
    did: int = Field(..., description="장식 ID")
    acquired_at: datetime = Field(..., description="장식 획득 시간 (ISO 8601 포맷)")
    is_equipped: bool = Field(..., description="장식 장착 여부")
    type: DecorationType = Field(..., description="장식 타입")

    # Decoration의 필드
    name: str = Field(..., max_length=50, description="장식 이름")
    version: int = Field(..., description="장식 버전")
    color: Optional[str] = Field(
        None, description="JSON String. 장식 색상(Asset 타입에만 해당)"
    )

    class Config:
        model_config = {"extra": "allow"}

    @field_validator("acquired_at")
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            # 타임존이 없는 경우 UTC로 설정
            return v.replace(tzinfo=timezone.utc)
        return v

    @classmethod
    def from_decoration_user(
        cls, decoration_user: DecorationUserInDB, decoration: DecorationInDB
    ) -> "DecorationUserWithDetails":
        """DecorationUser와 Decoration을 합성하여 새로운 모델 생성"""
        return cls(
            did=decoration_user.did,
            acquired_at=decoration_user.acquired_at,
            is_equipped=decoration_user.is_equipped,
            type=decoration_user.type,
            name=decoration.name,
            version=decoration.version,
            color=decoration.color,
        )


class UIDDecorationUserRequest(BaseModel):
    """
    사용자가 가지고 있는 모든 Decoration 관련 정보 조회 모델
    - uid: 사용자 ID
    """

    uid: int = Field(..., description="사용자 ID")


class GetDecorationUserResponse(BaseModel):
    decorations: List[DecorationUserWithDetails] = Field(
        ..., description="사용자가 가지고 있는 장식 목록"
    )


class CreateDecorationUserResponse(BaseModel):
    """
    사용자가 Decoration을 얻을 때 응답 모델
    """

    decoration_user: DecorationUserInDB = Field(..., description="장식 사용자 정보")


# 장착, 해제 요청 모델 (patch)
class EquipDecorationUserRequest(BaseModel):
    """
    사용자가 Decoration을 장착, 해제할 때 모델
    - uid: 사용자 ID
    - did: 장식 ID
    """

    uid: int = Field(..., description="사용자 ID")
    did: int = Field(..., description="장식 ID")


class EquipDecorationUserResponse(BaseModel):
    """
    사용자가 Decoration을 장착, 해제할 때 응답 모델
    - uid: 사용자 ID
    - did: 장식 ID
    """

    decoration_user: DecorationUserWithDetails = Field(
        ..., description="장식 사용자 정보"
    )
