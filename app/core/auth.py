from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.config import settings
from app.models.user_model import User
from app.services.user_service import UserService

# OAuth2 인증 스키마 - 모든 라우터에서 공통으로 사용
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """JWT 토큰에서 현재 사용자 정보 가져오기"""
    user = await UserService.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """현재 사용자가 활성 상태인지 확인"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="비활성화된 사용자"
        )
    return current_user


# admin 계정인지 확인하는 의존성
async def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """현재 사용자가 관리자인지 확인"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다. 관리자 권한이 필요합니다.",
        )
    return current_user


async def verify_superuser_token(token: str = Depends(oauth2_scheme)) -> Optional[bool]:
    """관리자 권한을 가진 사용자만 접근할 수 있는 엔드포인트"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await UserService.get_user_by_email(email)
        if not user or not user.is_active or not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Error verifying superuser token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"WWW-Authenticate": "Bearer"},
        )
