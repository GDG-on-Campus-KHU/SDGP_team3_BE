from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.database import execute_many, execute_query, fetch_all, fetch_one
from app.models.challenge_stamp_model import ChallengeStampInDB


class ChallengeStampRepository:
    """ChallengeStamp 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _map_row_to_challenge_stamp_in_db(
        row: Dict[str, Any],
    ) -> ChallengeStampInDB:
        """데이터베이스 행을 ChallengeStampInDB 모델로 변환"""
        # if not row:
        #     return None
        return ChallengeStampInDB(
            cid=row["cid"],
            sid=row["sid"],
        )

    @staticmethod
    async def create_challenge_stamp(
        challenge_ids: List[int],
        stamp_id: int,
    ) -> Optional[List[ChallengeStampInDB]]:
        """챌린지 스탬프 생성 메서드"""
        challenge_stamp_data = [(cid, stamp_id) for cid in challenge_ids]

        query = """
            INSERT INTO challenge_stamp (cid, sid)
            VALUES ($1, $2)
            RETURNING *
        """

        affected_rows = []
        for entity in challenge_stamp_data:
            affected_rows.append(await fetch_one(query, entity))

        if not affected_rows:
            return None
        elif len(affected_rows) != len(challenge_ids):
            print("[ERROR] Affected rows do not match the number of challenge IDs.")
            return None

        print(f"[INFO] Affected rows length: {len(affected_rows)}")
        return [
            ChallengeStampRepository._map_row_to_challenge_stamp_in_db(row)
            for row in affected_rows
            if row is not None
        ]
        # return ChallengeStampRepository._map_row_to_challenge_stamp_in_db(row)

    @staticmethod
    async def delete_challenge_stamp(
        challenge_ids: List[int],
        stamp_id: int,
    ) -> Optional[List[ChallengeStampInDB]]:
        """챌린지 스탬프 삭제 메서드"""
        query = """
            DELETE FROM challenge_stamp
            WHERE cid = ANY($1) AND sid = $2
            RETURNING *
        """
        values = (challenge_ids, stamp_id)
        rows = await fetch_all(query, values)
        if not rows:
            return None
        elif len(rows) != len(challenge_ids):
            print("[ERROR] Affected rows do not match the number of challenge IDs.")
            return None

        print(f"[INFO] Deleted rows length: {len(rows)}")
        return [
            ChallengeStampRepository._map_row_to_challenge_stamp_in_db(row)
            for row in rows
            if row is not None
        ]
