import traceback
from datetime import datetime
from typing import List, Optional

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
from app.models.challenge_model import ChallengeCreate, ChallengeInDB, ChallengeResponse
from app.models.stamp_model import (
    OrderDetails,
    StampCreate,
    StampInDB,
    StampResponse,
    StampType,
    Tumbler,
)
from app.models.user_model import User
from app.services.challenge_service import ChallengeService
from app.services.stamp_service import StampService
from app.services.vision_service import VisionService


def vision_api_verify(file: UploadFile, stamp_type: StampType) -> bool:
    """
    Mock Google Vision API verification function.
    In a real-world scenario, this function would call the Google Vision API to verify the stamp.
    """
    # Simulate verification logic
    if stamp_type == StampType.ORDER_DETAILS:
        # Simulate verification logic for order details
        res_od = VisionService.detect_spoon_fork_from_image(file=file)
        return True if res_od == "X" else False
    elif stamp_type == StampType.TUMBLER:
        # Simulate verification logic for tumbler
        res_tb = VisionService.detect_tumbler_in_image(file=file)
        return True if res_tb == "Tumbler" else False
    else:
        # Invalid stamp type
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid stamp type provided.",
        )


router = APIRouter(
    prefix="/api/stamps",
    tags=["stamps"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/{stamp_type}",
    response_model=List[ChallengeResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_stamp(
    stamp_type: StampType,
    saved_at: datetime = Form(...),
    uid: int = Form(...),
    challenges_ids_json: str = Form(...),  # JSON 문자열로 받음
    file: UploadFile = File(...),
    user: User = Depends(get_current_active_user),
) -> Optional[List[ChallengeResponse]]:
    """
    stamp 생성 엔드포인트
    - stamp_type: 스탬프 타입 (order_details, tumbler)

    ** challenges_json은 1,2,3 와 같은 challenge ids를 쉼표(,) 형태로 연결되도록 전달됨.

    1. stamp_type에 따른 stamp 선인증 (google vision api)
    2. stamp DB 생성 (url은 임시로 넣기)
    3. stamp file을 id와 filename을 이용하여 Object Storage에 저장
    4. stamp DB에 url 업데이트
    5. 챌린지와 stamp를 함께 return
    """

    # user_id가 uid와 일치하는지 확인
    if user.id != uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자 ID가 일치하지 않습니다.",
        )

    # 1. stamp_type에 따른 stamp 선인증 (google vision api)
    vision_api_verify_result = vision_api_verify(file, stamp_type)
    print(f"COMPLETED: vision_api_verify_result: {vision_api_verify_result}")
    if not vision_api_verify_result:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="스탬프 인증에 실패하여 변화가 없습니다.",
        )

    # 2. stamp DB 생성 (url은 임시로 넣기)
    try:
        challenges_ids_list = list(
            map(int, challenges_ids_json.split(","))
        )  # JSON 문자열을 리스트로 변환
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"challenges_ids_json 변환 시에 오류가 발생했습니다. '1,2,3'과 같이 받아야 합니다. 현재 값: {challenges_ids_json}",
        )

    stamp_data = StampCreate(
        saved_at=saved_at,
        type=stamp_type,
        save_url="no-url",
        challenge_ids=challenges_ids_list,
    )

    try:
        stamp = await StampService.create_stamp(uid=user.id, stamp_data=stamp_data)
        if not stamp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="스탬프 생성에 실패했습니다.",
            )
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"스탬프 생성 중 오류가 발생했습니다: {str(e)}",
        )

    # TODO: 2. stamp file을 id와 filename을 이용하여 Object Storage에 저장
    # TODO: 3. stamp DB에 url 업데이트

    # 4. 챌린지와 stamp를 함께 return
    try:
        challenges_with_stamps = (
            await ChallengeService.get_challenge_response_by_challenge_ids(
                challenge_ids=challenges_ids_list
            )
        )
        if challenges_with_stamps is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="챌린지와 스탬프 동시 조회에 실패했습니다.",
            )

        challenges_with_stamps = [
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
                stamps=challenge.stamps,
                type=StampType.ORDER_DETAILS if challenge.od_obj else StampType.TUMBLER,
            )
            for challenge in challenges_with_stamps
        ]

        print(f"COMPLETED: challenges_with_stamps: {challenges_with_stamps}")
        if not challenges_with_stamps:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="챌린지 조회에 실패했습니다.",
            )
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"챌린지 조회 중 오류가 발생했습니다: {str(e)}",
        )

    return challenges_with_stamps


@router.get("/", response_model=List[StampResponse], status_code=status.HTTP_200_OK)
async def get_stamp(
    user: User = Depends(get_current_active_user),
) -> Optional[List[StampResponse]]:
    """
    Stamp 조회 엔드포인트
    """
    try:
        stamps = await StampService.get_stamp_by_uid(user.id)
        if not stamps:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"스탬프 조회 중 오류가 발생했습니다: {str(e)}",
        )
    try:
        stamps_response = [
            StampResponse.timestamp_to_datestr(
                id=stamp.id,
                saved_at=stamp.saved_at,
                save_url=stamp.save_url,
                type=stamp.type,
            )
            for stamp in stamps
        ]
        return stamps_response
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"스탬프 응답 변환 중 오류가 발생했습니다: {str(e)}",
        )
