import glob
import os
from typing import List, Optional, Tuple

from fastapi import UploadFile

from app.models.challenge_model import ChallengeCreate, ChallengeInDB, ChallengeResponse
from app.models.stamp_model import StampBase, StampCreate, StampInDB, StampResponse
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.challenge_stamp_repository import ChallengeStampRepository
from app.repositories.stamp_repository import StampRepository


class StampService:
    """StampService는 챌린지 관련 비즈니스 로직을 처리하는 서비스입니다."""

    @staticmethod
    async def create_stamp(
        uid: int,
        stamp_data: StampCreate,
    ) -> Optional[StampInDB]:
        """챌린지 스탬프 생성 메서드"""
        # 챌린지 스탬프 생성
        stamp_base_data = StampBase(
            saved_at=stamp_data.saved_at,
            save_url=stamp_data.save_url,
            type=stamp_data.type,
        )
        stamp = await StampRepository.create_stamp(stamp_base_data)
        print(f"stamp: {stamp}")
        if not stamp:
            raise Exception("Failed to create stamp")

        # 챌린지 스탬프 생성 후 챌린지에 업데이트
        challenges = await ChallengeRepository.increment_challenge_achievements(
            uid=uid,
            challenge_ids=stamp_data.challenge_ids,
            stamp_type=stamp_data.type,
        )

        if not challenges:
            # 챌린지 업데이트 실패 시 스탬프 삭제
            print("DELETE STAMP - Failed to create stamp")
            deleted_stamp = await StampRepository.delete_stamp(stamp.id)
            raise Exception("Failed to update challenge achievements / Deleted stamp")

        challenge_stamp = await ChallengeStampRepository.create_challenge_stamp(
            challenge_ids=stamp_data.challenge_ids,
            stamp_id=stamp.id,
        )

        if not challenge_stamp:
            # 챌린지 스탬프 생성 실패 시 스탬프 삭제
            deleted_stamp = await StampRepository.delete_stamp(stamp.id)
            # 챌린지 스탬프는 ON DELETE CASCADE로 설정되어 있어 자동 삭제됨!
            # 챌린지 업데이트 롤백
            try:
                rollback_challenges = (
                    await ChallengeRepository.rollback_challenge_achivements(
                        challenges=challenges,
                        stamp_type=stamp_data.type,
                    )
                )
            except Exception as e:
                # 롤백 실패
                print("[FATAL] Failed to rollback challenge achievement. detail: {e}")
                raise Exception(
                    f"Failed to create challenge stamp / Deleted stamp: detail: {e}"
                )

        return stamp

    @staticmethod
    async def get_stamp_by_uid(
        uid: int,
    ) -> Optional[List[StampInDB]]:
        """UID로 스탬프 조회 메서드"""
        stamps = await StampRepository.get_stamp_by_uid(uid)
        if not stamps:
            return None
        print(f"stamp 개수: {len(stamps)}")
        return stamps
