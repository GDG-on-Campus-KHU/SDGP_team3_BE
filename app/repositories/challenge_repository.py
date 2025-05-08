from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.database.database import execute_query, fetch_all, fetch_one
from app.models.challenge_model import ChallengeCreate, ChallengeInDB, ChallengeResponse
from app.models.stamp_model import StampInDB, StampResponse, StampType
from app.repositories.stamp_repository import StampRepository


class ChallengeRepository:
    """Challenge 데이터 처리를 담당하는 리포지토리 클래스"""

    @staticmethod
    def _map_row_to_challenge_in_db(
        row: Dict[str, Any],
    ) -> ChallengeInDB:
        """데이터베이스 행을 ChallengeInDB 모델로 변환"""
        return ChallengeInDB(
            id=row["id"],
            uid=row["uid"],
            title=row["title"],
            description=row["description"],
            is_done=row["is_done"],
            od_obj=row["od_obj"],
            od_ach=row["od_ach"],
            tb_obj=row["tb_obj"],
            tb_ach=row["tb_ach"],
            start_at=row["start_at"],
            due_at=row["due_at"],
        )

    @staticmethod
    def _map_row_to_challenge_response(
        row: Dict[str, Any],
    ) -> ChallengeResponse:
        """데이터베이스 행을 ChallengeResponse 모델로 변환"""
        return ChallengeResponse(
            id=row["id"],
            uid=row["uid"],
            title=row["title"],
            description=row["description"],
            is_done=row["is_done"],
            od_obj=row.get("od_obj"),
            od_ach=row.get("od_ach"),
            tb_obj=row.get("tb_obj"),
            tb_ach=row.get("tb_ach"),
            start_at=row["start_at"],
            due_at=row["due_at"],
            stamps=row["stamps"],  # 스탬프 정보 추가
        )

    @staticmethod
    def _map_rows_to_challenge_with_stamps(
        rows: List[Dict[str, Any]],
    ) -> List[ChallengeResponse]:
        """여러 데이터베이스 행을 ChallengeResponse 모델로 변환"""
        # 챌린지 ID 별로 스탬프를 그룹화
        cid_map = defaultdict(list)
        # key: cid, value: idx
        cid_ctypes = {}
        # key: cid, value: stamp type
        for idx, row in enumerate(rows):
            cid = row["id"]
            cid_map[cid].append(idx)
            if row.get("od_obj") is not None:
                cid_ctypes[cid] = StampType.ORDER_DETAILS
            elif row.get("tb_obj") is not None:
                cid_ctypes[cid] = StampType.TUMBLER

        challenges_with_stamps = []
        print(f"rows:", rows)

        stamps: Optional[List[StampResponse]] = None  # 초기에 None으로 설정
        for cid, idx_list in cid_map.items():
            first_idx = idx_list[0]
            for idx in idx_list:
                # 스탬프 정보가 있는 경우에만 추가
                if rows[idx].get("sid") is not None:
                    if stamps is None:  # None일 경우 빈 리스트로 초기화
                        stamps = []
                    print(f"rows[idx]:", rows[idx])
                    stamps.append(
                        StampResponse(
                            id=rows[idx]["sid"],
                            type=StampRepository._type_string_mapper(rows[idx]["type"]),
                            saved_at=rows[idx]["saved_at"],
                            save_url=rows[idx]["save_url"],
                        )
                    )

            challenge_with_stamp = ChallengeResponse(
                id=cid,
                uid=rows[first_idx]["uid"],
                title=rows[first_idx]["title"],
                description=rows[first_idx]["description"],
                is_done=rows[first_idx]["is_done"],
                od_ach=rows[first_idx]["od_ach"],
                od_obj=rows[first_idx]["od_obj"],
                tb_ach=rows[first_idx]["tb_ach"],
                tb_obj=rows[first_idx]["tb_obj"],
                start_at=rows[first_idx]["start_at"],
                due_at=rows[first_idx]["due_at"],
                stamps=stamps,  # 스탬프 정보 추가
                type=cid_ctypes[cid],  # 스탬프 타입 추가
            )
            challenges_with_stamps.append(challenge_with_stamp)

        return challenges_with_stamps

    @staticmethod
    async def create_challenge(
        challenge_data: ChallengeCreate,
    ) -> Optional[ChallengeInDB]:
        """챌린지 생성 메서드"""
        query = """
            INSERT INTO challenges (uid, title, description, od_obj, od_ach, tb_obj, tb_ach, start_at, due_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING *
        """
        values = (
            challenge_data.uid,
            challenge_data.title,
            challenge_data.description,
            challenge_data.od_obj,
            challenge_data.od_ach,
            challenge_data.tb_obj,
            challenge_data.tb_ach,
            challenge_data.start_at,
            challenge_data.due_at,
        )
        row = await fetch_one(query, values)
        return ChallengeRepository._map_row_to_challenge_in_db(row)

    @staticmethod
    async def get_challenge_by_uid(uid: int) -> Optional[List[ChallengeInDB]]:
        """uid로 챌린지 조회 메서드"""
        query = """
            SELECT * FROM challenges WHERE uid = $1
        """
        values = (uid,)
        rows = await fetch_all(query, values)
        if not rows:
            return None
        return [
            ChallengeRepository._map_row_to_challenge_in_db(row)
            for row in rows
            if row is not None
        ]

    @staticmethod
    async def get_challenge_response_by_uid(uid: int) -> Optional[List[ChallengeInDB]]:
        """uid로 챌린지 및 스탬프 조회 메서드"""
        # 챌린지와 챌린지_스탬프, 스탬프 테이블을 조인하여 조회
        query = """
            SELECT s.id AS sid, s.type, s.saved_at, s.save_url, c.*
            FROM challenges AS c
            LEFT JOIN challenge_stamp AS cs ON c.id = cs.cid
            LEFT JOIN stamps AS s ON cs.sid = s.id
            WHERE c.uid = $1
        """
        values = (uid,)
        rows = await fetch_all(query, values)
        if not rows:
            return None

        return ChallengeRepository._map_rows_to_challenge_with_stamps(rows)

    @staticmethod
    async def rollback_challenge_achivements(
        challenges: List[ChallengeInDB],
        stamp_type: StampType,
    ) -> Optional[List[ChallengeInDB]]:
        """챌린지 달성 수 관련 업데이트 메서드"""
        # 챌린지 달성 수 감소 및 완료 여부 업데이트
        query = """
            UPDATE challenges
            SET {stamp_type}_ach = {stamp_type}_ach - 1,
                is_done = FALSE
            WHERE id = ANY($1)
                AND {stamp_type}_ach IS NOT NULL
                AND {stamp_type}_obj IS NOT NULL
            RETURNING *
        """
        if stamp_type == StampType.ORDER_DETAILS:
            query = query.format(stamp_type="od")
        elif stamp_type == StampType.TUMBLER:
            query = query.format(stamp_type="tb")
        else:
            raise ValueError("Invalid stamp type")
        values = ([challenge.id for challenge in challenges],)
        rows = await fetch_all(query, values)
        if not rows:
            return None
        return [
            ChallengeRepository._map_row_to_challenge_in_db(row)
            for row in rows
            if row is not None
        ]

    @staticmethod
    async def increment_challenge_achievements(
        uid: int,
        challenge_ids: List[int],
        stamp_type: StampType,
    ) -> Optional[List[ChallengeInDB]]:
        """챌린지 달성 수 업데이트 메서드"""
        query = """
            UPDATE challenges
            SET {stamp_type}_ach = {stamp_type}_ach + 1,
                is_done = CASE
                            WHEN {stamp_type}_ach + 1 = {stamp_type}_obj THEN TRUE
                            ELSE is_done
                        END
            WHERE id = ANY($1)
                AND uid = $2
                AND {stamp_type}_ach IS NOT NULL
                AND {stamp_type}_obj IS NOT NULL
                AND is_done = FALSE
            RETURNING *
        """
        if stamp_type == StampType.ORDER_DETAILS:
            query = query.format(stamp_type="od")
        elif stamp_type == StampType.TUMBLER:
            query = query.format(stamp_type="tb")
        else:
            raise ValueError("Invalid stamp type")

        values = (challenge_ids, uid)
        rows = await fetch_all(query, values)
        if not rows:
            return None
        return [
            ChallengeRepository._map_row_to_challenge_in_db(row)
            for row in rows
            if row is not None
        ]

    @staticmethod
    async def get_challenge_response_by_challenge_ids(
        challenge_ids: List[int],
    ) -> Optional[List[ChallengeResponse]]:
        """챌린지 ID로 스탬프 조회 메서드"""
        query = """
            SELECT s.id AS sid, s.type, s.saved_at, s.save_url, c.*
            FROM challenges AS c
            INNER JOIN challenge_stamp AS cs ON c.id = cs.cid
            INNER JOIN stamps AS s ON cs.sid = s.id
            WHERE c.id = ANY($1)
        """
        values = (challenge_ids,)
        rows = await fetch_all(query, values)
        if not rows:
            return None

        return ChallengeRepository._map_rows_to_challenge_with_stamps(rows)
