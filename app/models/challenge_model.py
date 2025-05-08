import enum
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, NewType, Optional, Union

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.stamp_model import StampInDB, StampResponse, StampType


class ChallengeBase(BaseModel):
    """ChallengeBase 기본 정보 모델"""

    uid: int
    title: str
    description: Optional[str]
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    od_obj: Optional[int] = Field(default=None, description="주문상세 도전 목표 수")
    od_ach: Optional[int] = Field(default=None, description="주문상세 도전 달성 수")
    tb_obj: Optional[int] = Field(default=None, description="텀블로 도전 목표 수")
    tb_ach: Optional[int] = Field(default=None, description="텀블로 도전 달성 수")
    start_at: datetime = Field(..., description="시작 날짜")
    due_at: datetime = Field(..., description="종료 날짜")

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class ChallengeCreate(BaseModel):
    """Challenge 챌린지 생성 모델"""

    uid: int
    title: str
    description: Optional[str]
    od_obj: Optional[int] = Field(default=None, description="주문상세 도전 목표 수")
    od_ach: Optional[int] = Field(default=None, description="주문상세 도전 달성 수")
    tb_obj: Optional[int] = Field(default=None, description="텀블로 도전 목표 수")
    tb_ach: Optional[int] = Field(default=None, description="텀블로 도전 달성 수")
    start_at: datetime = Field(..., description="시작 날짜")
    due_at: datetime = Field(..., description="종료 날짜")


class ChallengeWithStamps(ChallengeBase):
    """Challenges와 Stamps 동시 조회 모델"""

    stamps: List[StampInDB]  # stamps

    class Config:
        orm_mode = True


class ChallengeResponse(BaseModel):
    """Challenge 챌린지 조회 모델"""

    id: int
    uid: int
    title: str
    description: Optional[str]
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    od_obj: Optional[int] = Field(default=None, description="주문상세 도전 목표 수")
    od_ach: Optional[int] = Field(default=None, description="주문상세 도전 달성 수")
    tb_obj: Optional[int] = Field(default=None, description="텀블로 도전 목표 수")
    tb_ach: Optional[int] = Field(default=None, description="텀블로 도전 달성 수")
    start_at: Union[str, datetime] = Field(..., description="시작 날짜")
    due_at: Union[str, datetime] = Field(..., description="종료 날짜")
    stamps: Optional[List[StampResponse]]  # stamps
    type: StampType = Field(..., description="스탬프에 따른 챌린지 타입")

    class Config:
        orm_mode = True

    @classmethod
    def timestamp_to_datestr(
        cls,
        id: int,
        uid: int,
        title: str,
        description: Optional[str],
        is_done: bool,
        od_obj: Optional[int],
        od_ach: Optional[int],
        tb_obj: Optional[int],
        tb_ach: Optional[int],
        start_at: Union[str, datetime],
        due_at: Union[str, datetime],
        stamps: Optional[List[StampInDB]],
        type: StampType,
    ) -> "ChallengeResponse":
        """타임스탬프를 날짜(YYYY-MM-DD)로 변환하는 메서드"""
        # datetime 객체를 YYYY-MM-DD 형식의 문자열로 변환
        # TODO: 원래는 Timezone, nation에 따라 변환이 필요함
        # str 타입인 경우 datetime으로 변환
        if isinstance(start_at, str):
            start_at_str = start_at
        elif isinstance(start_at, datetime):
            start_at_str = start_at.strftime("%Y-%m-%d")

        if isinstance(due_at, str):
            due_at_str = due_at
        elif isinstance(due_at, datetime):
            due_at_str = due_at.strftime("%Y-%m-%d")

        print(f"stamp: {stamps}")
        if not stamps:
            return cls(
                id=id,
                uid=uid,
                title=title,
                description=description,
                is_done=is_done,
                od_obj=od_obj,
                od_ach=od_ach,
                tb_obj=tb_obj,
                tb_ach=tb_ach,
                start_at=start_at_str,
                due_at=due_at_str,
                stamps=None,
                type=type,
            )
        else:
            return cls(
                id=id,
                uid=uid,
                title=title,
                description=description,
                is_done=is_done,
                od_obj=od_obj,
                od_ach=od_ach,
                tb_obj=tb_obj,
                tb_ach=tb_ach,
                start_at=start_at_str,
                due_at=due_at_str,
                stamps=[
                    StampResponse.timestamp_to_datestr(
                        id=stamp.id,
                        saved_at=stamp.saved_at,
                        save_url=stamp.save_url,
                        type=stamp.type,
                    )
                    for stamp in stamps
                ],
                type=type,
            )


class ChallengeCreateResponse(BaseModel):
    """Challenge 챌린지 생성 응답 모델"""

    id: int
    uid: int = Field(..., description="챌린지 소유자 ID")
    title: str = Field(..., description="챌린지 제목")
    description: str = Field(default=None, description="챌린지 설명")
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    od_obj: Optional[int] = Field(default=None, description="주문상세 도전 목표 수")
    od_ach: Optional[int] = Field(default=None, description="주문상세 도전 달성 수")
    tb_obj: Optional[int] = Field(default=None, description="텀블로 도전 목표 수")
    tb_ach: Optional[int] = Field(default=None, description="텀블로 도전 달성 수")
    start_at: Union[datetime, str] = Field(..., description="시작 날짜")
    due_at: Union[datetime, str] = Field(..., description="종료 날짜")

    @classmethod
    def timestamp_to_datestr(
        cls,
        id: int,
        uid: int,
        title: str,
        description: Optional[str],
        is_done: bool,
        od_obj: Optional[int],
        od_ach: Optional[int],
        tb_obj: Optional[int],
        tb_ach: Optional[int],
        start_at: datetime,
        due_at: datetime,
    ) -> "ChallengeCreateResponse":
        """타임스탬프를 날짜(YYYY-MM-DD)로 변환하는 메서드"""
        # datetime 객체를 YYYY-MM-DD 형식의 문자열로 변환
        return cls(
            id=id,
            uid=uid,
            title=title,
            description=description,
            is_done=is_done,
            od_obj=od_obj,
            od_ach=od_ach,
            tb_obj=tb_obj,
            tb_ach=tb_ach,
            start_at=start_at.strftime("%Y-%m-%d"),
            due_at=due_at.strftime("%Y-%m-%d"),
        )


class ChallengeInDB(ChallengeBase):
    """Challenge 챌린지 모델"""

    id: int
    uid: int = Field(..., description="챌린지 소유자 ID")
    title: str = Field(..., description="챌린지 제목")
    description: str = Field(default=None, description="챌린지 설명")
    is_done: bool = Field(default=False, description="챌린지 완료 여부")
    od_obj: Optional[int] = Field(default=None, description="주문상세 도전 목표 수")
    od_ach: Optional[int] = Field(default=None, description="주문상세 도전 달성 수")
    tb_obj: Optional[int] = Field(default=None, description="텀블로 도전 목표 수")
    tb_ach: Optional[int] = Field(default=None, description="텀블로 도전 달성 수")
    start_at: datetime = Field(..., description="시작 날짜")
    due_at: datetime = Field(..., description="종료 날짜")

    class Config:
        orm_mode = True
