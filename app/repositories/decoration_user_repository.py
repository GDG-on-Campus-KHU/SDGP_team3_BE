from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg

from app.database.database import execute_query, fetch_all, fetch_one
from app.models.decoration_model import DecorationInDB, DecorationType
from app.models.decoration_user_model import (
    DecorationUserInDB,
    DecorationUserWithDetails,
)
from app.models.user_model import User, UserCreate, UserInDB, UserUpdate


class DecorationUserRepository:
    """DecorationUser 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _map_row_to_decoration_user_in_db(
        row: Dict[str, Any],
    ) -> Optional[DecorationUserInDB]:
        """데이터베이스 행을 DecorationInDB 모델로 변환"""
        if not row:
            return None
        return DecorationUserInDB(
            did=row["did"],
            uid=row["uid"],
            acquired_at=row["acquired_at"],
            is_equipped=row["is_equipped"],
            type=row["type"],
        )

    @staticmethod
    def _map_row_to_decoration_user_with_details(
        row: Dict[str, Any],
    ) -> Optional[DecorationUserWithDetails]:
        """데이터베이스 행을 DecorationUserWithDetails 모델로 변환"""
        if not row:
            return None
        return DecorationUserWithDetails(
            did=row["did"],
            acquired_at=row["acquired_at"],
            is_equipped=row["is_equipped"],
            type=row["type"],
            name=row["name"],
            version=row["version"],
            color=row.get("color"),
        )

    @staticmethod
    async def get_by_user_id(user_id: int) -> List[Optional[DecorationUserWithDetails]]:
        """사용자 ID로 DecorationUser 및 Decoration 조인 후 조회 메서드"""
        query = """
            SELECT du.did, du.acquired_at, du.is_equipped, du.type, d.name, d.version, d.color
            FROM decoration_user AS du
            INNER JOIN decorations AS d ON du.did = d.id
            WHERE du.uid = $1
        """
        values = (user_id,)
        rows = await fetch_all(query, values)
        return [
            DecorationUserRepository._map_row_to_decoration_user_with_details(row)
            for row in rows
        ]

    @staticmethod
    async def add_decoration_user(
        uid: int,
        did: int,
        decoration_type: str,
        acquired_at: datetime,
    ) -> Optional[DecorationUserInDB]:
        """장식 생성 메서드"""
        query = """
            INSERT INTO decoration_user (uid, did, type, acquired_at, is_equipped)
            VALUES ($1, $2, $3, $4, FALSE)
            RETURNING did, uid, acquired_at, is_equipped, type
        """
        try:
            values = (uid, did, decoration_type, acquired_at)
            row = await fetch_one(query, values)
        except asyncpg.exceptions.UniqueViolationError:
            # 장식이 이미 존재하는 경우
            raise ValueError("Decoration already exists for this user.")
        except Exception as e:
            # 다른 예외 처리
            raise ValueError(f"An error occurred: {str(e)}")

        return DecorationUserRepository._map_row_to_decoration_user_in_db(row)

    @staticmethod
    async def draw_random_decoration(
        uid: int,
    ) -> Optional[DecorationInDB]:
        """사용자가 갖지 않은 랜덤 장식 조회 메서드"""
        query = """
            SELECT d.*
            FROM decorations AS d
            WHERE d.id NOT IN (SELECT did FROM decoration_user WHERE uid = $1)
            ORDER BY RANDOM()
            LIMIT 1
            """
        values = (uid,)
        row = await fetch_one(query, values)
        # 모두 가지고 있는 경우.
        if not row:
            return None
        return DecorationInDB(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            rarity=row["rarity"],
            type=row["type"],
            color=row["color"],
        )

    @staticmethod
    async def equip_decoration_user(
        uid: int,
        did: int,
        type: DecorationType,
    ) -> Optional[DecorationUserInDB]:
        """장식 장착 여부 업데이트 메서드"""
        query = """
            UPDATE decoration_user
            SET is_equipped = NOT is_equipped
            WHERE uid = $1 AND did = $2 AND type = $3
            RETURNING did, uid, acquired_at, is_equipped, type
        """
        values = (uid, did, type)
        row = await fetch_one(query, values)
        if not row:
            return None
        return DecorationUserRepository._map_row_to_decoration_user_in_db(row)
