from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg

from app.database.database import execute_query, fetch_all, fetch_one
from app.models.decoration_model import Asset, Decoration, DecorationInDB, Landscape
from app.models.user_model import User, UserCreate, UserInDB, UserUpdate


class DecorationRepository:
    """Decoration 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _map_row_to_decoration_in_db(row: Dict[str, Any]) -> Optional[DecorationInDB]:
        """데이터베이스 행을 DecorationInDB 모델로 변환"""
        if not row:
            return None
        return DecorationInDB(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            type=row["type"],
            rarity=row["rarity"],
            color=row.get("color"),  # Asset 타입에만 해당
        )

    @staticmethod
    def _map_row_to_decoration(row: Dict[str, Any]) -> Optional[Decoration]:
        """데이터베이스 행을 Decoration 모델로 변환"""
        if not row:
            return None
        return Decoration(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            type=row["type"],
            rarity=row["rarity"],
            color=row.get("color"),  # Asset 타입에만 해당
        )

    @staticmethod
    def _map_row_to_landscape(row: Dict[str, Any]) -> Optional[Landscape]:
        """데이터베이스 행을 Landscape 모델로 변환"""
        if not row:
            return None
        return Landscape(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            type=row["type"],
            rarity=row["rarity"],
        )

    @staticmethod
    def _map_row_to_asset(row: Dict[str, Any]) -> Optional[Asset]:
        """데이터베이스 행을 Asset 모델로 변환"""
        if not row:
            return None
        return Asset(
            id=row["id"],
            name=row["name"],
            version=row["version"],
            type=row["type"],
            rarity=row["rarity"],
            color=row["color"],  # json string 색상 코드 (예: "#FF5733")
        )

    @staticmethod
    async def create_landscape(landscape_data: Landscape) -> Optional[Landscape]:
        """Landscape 장식 생성"""
        try:
            query = """
                INSERT INTO decorations (name, version, type, rarity)
                VALUES ($1, $2, $3, $4)
                RETURNING id, name, version, type, rarity
            """
            values = (
                landscape_data.name,
                landscape_data.version,
                landscape_data.type,
                landscape_data.rarity,
            )

            row = await fetch_one(query, values)
            return DecorationRepository._map_row_to_landscape(row)
        except asyncpg.exceptions.UniqueViolationError:
            # 중복된 장식 이름
            print("[ERROR] Duplicate decoration name!")
            return None
        except Exception as e:
            print(f"[ERROR] Create Landscape insert in DB: {e}")
            return None

    @staticmethod
    async def create_asset(asset_data: Asset) -> Optional[Asset]:
        """Asset 장식 생성"""
        try:
            query = """
                INSERT INTO decorations (name, version, type, rarity, color)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, name, version, type, rarity, color
            """
            values = (
                asset_data.name,
                asset_data.version,
                asset_data.type,
                asset_data.rarity,
                asset_data.color,
            )

            row = await fetch_one(query, values)
            return DecorationRepository._map_row_to_asset(row)
        except asyncpg.exceptions.UniqueViolationError:
            # 중복된 장식 이름
            print("[ERROR] Duplicate decoration name!")
            return None
        except Exception as e:
            print(f"[ERROR] Insert asset in DB: {e}")
            return None

    @staticmethod
    async def get_all_decorations() -> List[Optional[DecorationInDB]]:
        """모든 장식 조회"""
        query = """
            SELECT id, name, version, type, rarity, color
            FROM decorations
        """
        rows = await fetch_all(query)
        return [DecorationRepository._map_row_to_decoration_in_db(row) for row in rows]
