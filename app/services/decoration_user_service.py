from datetime import datetime, timezone
from typing import List, Optional, Tuple
from zoneinfo import ZoneInfo

from app.models.decoration_model import DecorationInDB, DecorationType
from app.models.decoration_user_model import (
    DecorationUserInDB,
    DecorationUserWithDetails,
)
from app.repositories.decoration_user_repository import DecorationUserRepository


class DecorationUserService:
    """DecorationUserService는 유저가 가진 장식 관련 비즈니스 로직을 처리하는 서비스입니다."""

    @staticmethod
    async def get_by_user_id(user_id: int) -> List[DecorationUserWithDetails]:
        """사용자 ID로 장식 조회 메서드"""
        user_decoration = await DecorationUserRepository.get_by_user_id(user_id)
        filtered: List[DecorationUserWithDetails] = [
            decoration_with_details
            for decoration_with_details in user_decoration
            if decoration_with_details != None
        ]
        return filtered

    @staticmethod
    async def add_decoration_user(
        uid: int,
        did: int,
        decoration_type: DecorationType,
    ) -> Optional[DecorationUserInDB]:
        """장식 생성 메서드"""
        # TODO: 현재 기본 타임존은 Asia/Seoul로 설정
        tz = ZoneInfo("Asia/Seoul")
        acquired_at = datetime.now(tz=tz)
        print(f"[WARNING] 아직 시간대가 설정되지 않았습니다. 기본 시간대는 {tz}입니다.")
        decoration_user = await DecorationUserRepository.add_decoration_user(
            uid, did, decoration_type, acquired_at
        )
        if not decoration_user:
            raise ValueError("장식 생성에 실패했습니다.")
        return decoration_user

    @staticmethod
    async def draw_random_decoration(uid: int) -> DecorationInDB:
        """사용자가 갖지 않은 랜덤 장식 조회 메서드"""
        # 랜덤 장식 조회
        decoration = await DecorationUserRepository.draw_random_decoration(uid)
        if not decoration:
            raise ValueError(
                "랜덤 장식을 찾을 수 없거나 사용자가 모두 가지고 있습니다."
            )
        return decoration

    @staticmethod
    async def equip_decoration_user(
        uid: int,
        did: int,
        type: DecorationType,
    ) -> Optional[DecorationUserInDB]:
        """장식 장착 여부 업데이트 메서드"""
        decoration_user = await DecorationUserRepository.equip_decoration_user(
            uid, did, type
        )
        if not decoration_user:
            raise ValueError("장식 장착 여부 업데이트에 실패했습니다.")
        return decoration_user

    # 전부 다 디버깅 필요.
