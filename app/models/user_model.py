from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """사용자 기본 정보 모델"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """사용자 생성 모델"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """사용자 업데이트 모델"""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """데이터베이스 내 사용자 모델"""

    id: int
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


class User(UserBase):
    """공개 사용자 모델"""

    id: int
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserLogin(BaseModel):
    """사용자 로그인 모델"""

    email: EmailStr
    password: str


# 챌린지와 데코레이션
class Challenge(BaseModel):
    id: int
    title: str
    completed: bool


class Decoration(BaseModel):
    id: int
    type: str
    name: str
