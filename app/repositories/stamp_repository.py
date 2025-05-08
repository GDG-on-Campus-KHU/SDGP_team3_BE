from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.database.database import execute_query, fetch_all, fetch_one
from app.models.challenge_model import ChallengeCreate, ChallengeInDB, ChallengeResponse
from app.models.stamp_model import (
    StampBase,
    StampCreate,
    StampInDB,
    StampResponse,
    StampType,
)


class StampRepository:
    """Stamp 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _type_string_mapper(
        stamp_type: Union[StampType, str],
    ) -> Union[StampType, str, None]:
        """스탬프 타입:문자열 전환기"""
        if isinstance(stamp_type, StampType):
            if stamp_type == StampType.TUMBLER:
                return "tb"
            elif stamp_type == StampType.ORDER_DETAILS:
                return "od"
            else:
                raise ValueError("Invalid stamp type")
        elif isinstance(stamp_type, str):
            if stamp_type == "tb":
                return StampType.TUMBLER
            elif stamp_type == "od":
                return StampType.ORDER_DETAILS
            else:
                raise ValueError("Invalid stamp type")

    @staticmethod
    def _map_row_to_stamp_in_db(
        row: Dict[str, Any],
    ) -> StampInDB:
        """데이터베이스 행을 StampInDB 모델로 변환"""
        # if not row:
        #     return None
        return StampInDB(
            id=row["id"],
            type=StampRepository._type_string_mapper(row["type"]),
            save_url=row["save_url"],
            saved_at=row["saved_at"],
        )

    @staticmethod
    def _map_row_to_stamp_response_datestr(
        row: Dict[str, Any],
    ) -> StampResponse:
        """데이터베이스 행을 StampResponse 모델로 변환"""
        # if not row:
        #     return None
        return StampResponse.timestamp_to_datestr(
            id=row["id"],
            type=row["type"],
            save_url=row["save_url"],
            saved_at=row["saved_at"].strftime("%Y-%m-%d"),
        )

    @staticmethod
    async def get_stamp_by_uid(
        uid: int,
    ) -> Optional[List[StampInDB]]:
        """스탬프 조회 메서드"""
        query = """
            SELECT s.*
            FROM stamps AS s
            INNER JOIN challenge_stamp AS cs ON s.id = cs.sid
            INNER JOIN challenges AS c ON cs.cid = c.id
            WHERE c.uid = $1
        """
        values = (uid,)
        rows = await fetch_all(query, values)
        if not rows:
            return None
        # 스탬프를 StampInDB 모델로 변환
        return [
            StampRepository._map_row_to_stamp_in_db(row)
            for row in rows
            if row is not None
        ]

    @staticmethod
    async def create_stamp(
        stamp_data: StampBase,
    ) -> Optional[StampInDB]:
        """스탬프 생성 메서드"""
        query = """
            INSERT INTO stamps (saved_at, save_url, type)
            VALUES ($1, $2, $3)
            RETURNING *
        """
        type_value = StampRepository._type_string_mapper(stamp_data.type)
        values = (
            stamp_data.saved_at,
            stamp_data.save_url,
            type_value,
        )
        row = await fetch_one(query, values)
        print(f"row: {row}")
        if not row:
            return None
        return StampRepository._map_row_to_stamp_in_db(row)

    @staticmethod
    async def delete_stamp(
        stamp_id: int,
    ) -> Optional[StampInDB]:
        """스탬프 삭제 메서드"""
        query = """
            DELETE FROM stamps
            WHERE id = $1
            RETURNING *
        """
        values = (stamp_id,)
        row = await fetch_one(query, values)
        if not row:
            return None
        return StampRepository._map_row_to_stamp_in_db(row)
