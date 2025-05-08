import glob
import os
from typing import List, Optional, Tuple

from fastapi import UploadFile

from app.models.challenge_model import ChallengeCreate, ChallengeInDB, ChallengeResponse
from app.models.stamp_model import StampBase, StampCreate, StampInDB
from app.repositories.challenge_repository import ChallengeRepository


class ChallengeService:
    """ChallengeService는 챌린지 관련 비즈니스 로직을 처리하는 서비스입니다."""

    @staticmethod
    async def create_challenge(
        challenge_data: ChallengeCreate,
    ) -> Optional[ChallengeInDB]:
        """챌린지 생성 메서드"""
        # 챌린지 생성
        return await ChallengeRepository.create_challenge(challenge_data)

    @staticmethod
    async def get_challenge_by_uid(uid: int) -> Optional[List[ChallengeInDB]]:
        """챌린지 ID로 챌린지 조회 메서드"""
        return await ChallengeRepository.get_challenge_by_uid(uid)

    @staticmethod
    async def get_challenge_response_by_uid(
        uid: int,
    ) -> Optional[List[ChallengeResponse]]:
        """챌린지 ID로 챌린지 스탬프 조회 메서드"""
        return await ChallengeRepository.get_challenge_response_by_uid(uid)

    @staticmethod
    async def get_challenge_response_by_challenge_ids(
        challenge_ids: List[int],
    ) -> Optional[List[ChallengeResponse]]:
        """챌린지 ID로 챌린지 스탬프 조회 메서드"""
        return await ChallengeRepository.get_challenge_response_by_challenge_ids(
            challenge_ids
        )
