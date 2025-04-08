from typing import List, Optional, Dict, Any
import asyncpg
from passlib.context import CryptContext
from datetime import datetime

from app.models.user_model import User, UserCreate, UserUpdate, UserInDB
from app.database.database import fetch_one, fetch_all, execute_query

# 비밀번호 암호화를 위한 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    """사용자 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _hash_password(password: str) -> str:
        """비밀번호를 해시 처리"""
        return pwd_context.hash(password)

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def _map_row_to_user(row: Dict[str, Any]) -> Optional[User]:
        """데이터베이스 행을 User 모델로 변환"""
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            username=row["username"],
            is_active=row["is_active"],
            is_superuser=row["is_superuser"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    @staticmethod
    def _map_row_to_user_in_db(row: Dict[str, Any]) -> Optional[UserInDB]:
        """데이터베이스 행을 UserInDB 모델로 변환"""
        if not row:
            return None
        return UserInDB(
            id=row["id"],
            email=row["email"],
            username=row["username"],
            hashed_password=row["hashed_password"],
            is_active=row["is_active"],
            is_superuser=row["is_superuser"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    @staticmethod
    async def create_user(user_data: UserCreate) -> Optional[User]:
        """사용자 생성"""
        try:
            hashed_password = UserRepository._hash_password(user_data.password)
            
            query = """
                INSERT INTO users (email, username, hashed_password)
                VALUES ($1, $2, $3)
                RETURNING id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            """
            values = (user_data.email, user_data.username, hashed_password)
            
            row = await fetch_one(query, values)
            return UserRepository._map_row_to_user(row)
        except asyncpg.exceptions.UniqueViolationError:
            # 중복 이메일 또는 사용자 이름
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[User]:
        """ID로 사용자 조회"""
        query = """
            SELECT id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            FROM users
            WHERE id = $1
        """
        row = await fetch_one(query, (user_id,))
        return UserRepository._map_row_to_user(row)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserInDB]:
        """이메일로 사용자 조회 (비밀번호 해시 포함)"""
        query = """
            SELECT id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            FROM users
            WHERE email = $1
        """
        row = await fetch_one(query, (email,))
        return UserRepository._map_row_to_user_in_db(row)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """사용자 이름으로 사용자 조회"""
        query = """
            SELECT id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            FROM users
            WHERE username = $1
        """
        row = await fetch_one(query, (username,))
        return UserRepository._map_row_to_user(row)

    @staticmethod
    async def get_all_users() -> List[User]:
        """모든 사용자 조회"""
        query = """
            SELECT id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            FROM users
        """
        rows = await fetch_all(query)
        return [UserRepository._map_row_to_user(row) for row in rows]

    @staticmethod
    async def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]:
        """사용자 정보 업데이트"""
        # 현재 사용자 정보 가져오기
        current_user = await UserRepository.get_user_by_id(user_id)
        if not current_user:
            return None

        # 업데이트할 필드 구성
        update_fields = []
        update_values = []

        if user_data.email is not None:
            update_fields.append("email = $%d" % (len(update_values) + 1))
            update_values.append(user_data.email)

        if user_data.username is not None:
            update_fields.append("username = $%d" % (len(update_values) + 1))
            update_values.append(user_data.username)

        if user_data.password is not None:
            update_fields.append("hashed_password = $%d" % (len(update_values) + 1))
            update_values.append(UserRepository._hash_password(user_data.password))

        if user_data.is_active is not None:
            update_fields.append("is_active = $%d" % (len(update_values) + 1))
            update_values.append(user_data.is_active)

        # updated_at 필드 업데이트
        update_fields.append("updated_at = $%d" % (len(update_values) + 1))
        update_values.append(datetime.now())

        # user_id를 마지막 매개변수로 추가
        update_values.append(user_id)

        if not update_fields:
            return current_user  # 업데이트할 내용이, 없으면 현재 사용자 반환

        try:
            query = f"""
                UPDATE users
                SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ${len(update_values)}
                RETURNING id, email, username, hashed_password, is_active, is_superuser, created_at, updated_at
            """

            row = await fetch_one(query, tuple(update_values))
            return UserRepository._map_row_to_user(row)
        except asyncpg.exceptions.UniqueViolationError:
            # 중복 이메일 또는 사용자 이름
            return None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """사용자 삭제"""
        query = """
            DELETE FROM users
            WHERE id = $1
            RETURNING id
        """
        row = await fetch_one(query, (user_id,))
        return row is not None

    @staticmethod
    async def verify_user(email: str, password: str) -> Optional[User]:
        """사용자 이메일/비밀번호 확인"""
        user_in_db = await UserRepository.get_user_by_email(email)
        if not user_in_db:
            return None
        
        if not UserRepository._verify_password(password, user_in_db.hashed_password):
            return None
        
        # 비밀번호가 맞으면 User 모델로 변환하여 반환 (비밀번호 해시 제외)
        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            username=user_in_db.username,
            is_active=user_in_db.is_active,
            is_superuser=user_in_db.is_superuser,
            created_at=user_in_db.created_at,
            updated_at=user_in_db.updated_at
        )