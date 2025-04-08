from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# 사용자 생성 요청 DTO
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

# 사용자 업데이트 요청 DTO
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None

# 사용자 응답 DTO
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 사용자 인증 요청 DTO
class UserLogin(BaseModel):
    email: EmailStr
    password: str