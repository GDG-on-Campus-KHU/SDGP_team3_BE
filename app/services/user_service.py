from datetime import datetime, timedelta
from typing import List, Optional

from jose import JWTError, jwt

from app.config import settings
from app.models.user_model import User, UserCreate, UserLogin, UserUpdate
from app.repositories.user_repository import UserRepository


class UserService:
    """사용자 관련 비즈니스 로직을 담당하는 서비스 클래스"""

    @staticmethod
    async def create_user(user_data: UserCreate) -> Optional[User]:
        """사용자 생성 서비스"""
        # 이메일 중복 확인
        existing_user = await UserRepository.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("이미 존재하는 이메일입니다.")

        # 사용자 이름 중복 확인
        existing_username = await UserRepository.get_user_by_username(
            user_data.username
        )
        if existing_username:
            raise ValueError("이미 존재하는 사용자 이름입니다.")

        user = await UserRepository.create_user(user_data)
        if not user:
            raise ValueError("사용자 생성에 실패했습니다.")

        return user

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID로 사용자 조회 서비스"""
        return await UserRepository.get_user_by_id(user_id)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """이메일로 사용자 조회 서비스"""
        user_in_db = await UserRepository.get_user_by_email(email)
        if not user_in_db:
            return None

        # UserInDB를 User로 변환 (비밀번호 해시 제외)
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            is_superuser=user_in_db.is_superuser,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at,
        )

    @staticmethod
    async def get_all_users() -> List[User]:
        """모든 사용자 조회 서비스"""
        return await UserRepository.get_all_users()

    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 업데이트 서비스"""
        # 모델 유효성 검사 후 비어있지 않은 필드만 사용
        update_data = UserUpdate(
            **{k: v for k, v in user_data.model_dump().items() if v is not None}
        )

        if not any(user_data.model_dump().values()):
            raise ValueError("업데이트할 데이터가 없습니다.")

        # 이메일 업데이트 시 중복 확인
        if update_data.email:
            existing_user = await UserRepository.get_user_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("이미 존재하는 이메일입니다.")

        # 사용자 이름 업데이트 시 중복 확인
        if update_data.username:
            existing_user = await UserRepository.get_user_by_username(
                update_data.username
            )
            if existing_user and existing_user.id != user_id:
                raise ValueError("이미 존재하는 사용자 이름입니다.")

        user = await UserRepository.update_user(user_id, update_data)
        if not user:
            return None

        return user

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """사용자 삭제 서비스"""
        return await UserRepository.delete_user(user_id)

    @staticmethod
    async def authenticate_user(credentials: UserLogin) -> Optional[dict]:
        """사용자 인증 및 토큰 생성 서비스"""
        user = await UserRepository.verify_user(credentials.email, credentials.password)
        if not user:
            return None

        # 액세스 토큰 생성
        access_token = UserService.create_access_token(data={"sub": user.email})

        return {"access_token": access_token, "token_type": "bearer", "user": user}

    @staticmethod
    def create_access_token(data: dict) -> str:
        """JWT 액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})

        return str(
            jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        )

    @staticmethod
    async def get_current_user(token: str) -> Optional[User]:
        """토큰에서 현재 사용자 가져오기"""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None

        user = await UserRepository.get_user_by_email(email)
        if user is None:
            return None

        # UserInDB를 User로 변환
        return User(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
