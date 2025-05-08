from datetime import datetime
from typing import List, Optional, Union

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from app.core.auth import (
    get_current_active_user,
    get_current_superuser,
    verify_superuser_token,
)
from app.models.challenge_model import (
    ChallengeCreate,
    ChallengeCreateResponse,
    ChallengeInDB,
    ChallengeResponse,
)
from app.models.decoration_model import (
    Asset,
    AssetType,
    DecorationInDB,
    Landscape,
    LandscapeType,
)
from app.models.user_model import User
from app.services.challenge_service import ChallengeService
from app.services.decoration_service import DecorationService

router = APIRouter(
    prefix="/api/challenges",
    tags=["challenges"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/", response_model=ChallengeCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_challenge(
    challenge_data: ChallengeCreate,
    user: User = Depends(get_current_active_user),
) -> Optional[ChallengeCreateResponse]:
    """Challenge 생성 엔드포인트"""

    if user.id != challenge_data.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="자신의 챌린지만 생성할 수 있습니다.",
        )

    try:
        challenge = await ChallengeService.create_challenge(challenge_data)
        print(f"COMPLETED: challenge: {challenge}")
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="챌린지 생성에 실패했습니다.",
            )
        challenge = ChallengeCreateResponse.timestamp_to_datestr(
            id=challenge.id,
            uid=challenge.uid,
            title=challenge.title,
            description=challenge.description,
            is_done=challenge.is_done,
            od_obj=challenge.od_obj,
            od_ach=challenge.od_ach,
            tb_obj=challenge.tb_obj,
            tb_ach=challenge.tb_ach,
            start_at=challenge.start_at,
            due_at=challenge.due_at,
        )
        print(f"challenge: {challenge}")

        return challenge
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Form 데이터는 따로 Request model을 만들지 않음.
@router.get("/", response_model=List[ChallengeResponse], status_code=status.HTTP_200_OK)
async def get_challenges(
    user: User = Depends(get_current_active_user),
) -> Union[List[ChallengeResponse], Response]:
    """
    Challenge 조회 엔드포인트
    """
    # 챌린지 및 스탬프 한 번에 조회 (uid로)
    # uid로부터 챌린지 테이블을 먼저 조회하니 ChallengeService에서 처리
    challenge_with_stamps = await ChallengeService.get_challenge_response_by_uid(
        user.id
    )
    if not challenge_with_stamps:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    # 타임스탬프 변환
    try:
        challenge_with_stamps = [
            ChallengeResponse.timestamp_to_datestr(
                id=challenge.id,
                uid=challenge.uid,
                title=challenge.title,
                description=challenge.description,
                is_done=challenge.is_done,
                od_obj=challenge.od_obj,
                od_ach=challenge.od_ach,
                tb_obj=challenge.tb_obj,
                tb_ach=challenge.tb_ach,
                start_at=challenge.start_at,
                due_at=challenge.due_at,
                stamps=(
                    [stamp for stamp in challenge.stamps] if challenge.stamps else None
                ),  # 스탬프가 없는 경우, None으로 설정
            )
            for challenge in challenge_with_stamps
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"타임스탬프 변환 중 오류가 발생했습니다: {str(e)}",
        )
    else:
        # 변환된 챌린지 리스트를 반환
        print(f"COMPLETED: challenge_with_stamps: {challenge_with_stamps}")
        # 챌린지 리스트를 반환
        return challenge_with_stamps
