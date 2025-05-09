import traceback
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_active_user
from app.models.decoration_model import DecorationInDB, DecorationReference
from app.models.decoration_user_model import (
    CreateDecorationUserResponse,
    DecorationUserInDB,
    GetDecorationUserResponse,
    UIDDecorationUserRequest,
)
from app.models.user_model import User
from app.services.decoration_user_service import DecorationUserService

router = APIRouter(
    prefix="/api/users/decorations",  # localhost:80
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# 유저 개인의 것이니 api는 필요없음.
# 유저가 소유한 것이니 api/users/decorations/로 접근
@router.get("/", response_model=GetDecorationUserResponse)
async def get_user_decorations(
    user: User = Depends(get_current_active_user),
) -> GetDecorationUserResponse:
    """사용자의 장식 목록 조회 엔드포인트"""
    uid_request = UIDDecorationUserRequest(uid=user.id)
    try:
        decorations = await DecorationUserService.get_by_user_id(uid_request.uid)
        return GetDecorationUserResponse(decorations=decorations)
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"장식을 찾을 수 없습니다. {str(e)}",
        )


@router.post("/", response_model=CreateDecorationUserResponse)
async def add_decoration_user(
    uid_request: UIDDecorationUserRequest,
    decoration_ref: DecorationReference,
    user: User = Depends(get_current_active_user),
) -> CreateDecorationUserResponse:
    """장식 생성 엔드포인트"""

    if user.id != uid_request.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자 ID가 일치하지 않습니다.",
        )
    try:
        decoration_user = await DecorationUserService.add_decoration_user(
            uid_request.uid,
            decoration_ref.did,
            decoration_ref.type,
        )
        if not decoration_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="장식 생성에 실패했습니다.",
            )
        return CreateDecorationUserResponse(decoration_user=decoration_user)
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"장식 생성에 실패했습니다. {str(e)}",
        )


@router.post("/random", response_model=DecorationInDB)
async def draw_random_decoration(
    uid_request: UIDDecorationUserRequest,
    user: User = Depends(get_current_active_user),
) -> DecorationInDB:
    """
    사용자가 갖지 않은 랜덤 장식 뽑기 엔드포인트
    - uid, token 필요
    - return: 사용자가 얻은 랜덤 장식
    - 랜덤 장식은 DecorationInDB 모델로 반환
    """

    if user.id != uid_request.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자 ID가 일치하지 않습니다.",
        )
    try:
        random_decoration = await DecorationUserService.draw_random_decoration(
            uid_request.uid
        )
        if not random_decoration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="랜덤 장식을 찾을 수 없거나 사용자가 모두 가지고 있습니다.",
            )
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"랜덤 장식 뽑기 중 오류가 발생했습니다: {str(e)}",
        )

    # 랜덤 장식 유저 추가
    # TODO: 얻자마자 바로 장착한다면 여기 수정 필요!
    try:
        decoration_user = await DecorationUserService.add_decoration_user(
            uid_request.uid,
            random_decoration.id,
            random_decoration.type,
        )
        if not decoration_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="장식 생성에 실패했습니다.",
            )
    except Exception as e:
        print(f"ERROR: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"장식 생성에 실패했습니다. {str(e)}",
        )
    else:
        return random_decoration


@router.patch("/", response_model=DecorationUserInDB)
async def equip_decoration_user(
    uid_request: UIDDecorationUserRequest,
    decoration_ref: DecorationReference,
    user: User = Depends(get_current_active_user),
) -> DecorationUserInDB:
    """장식 장착, 해제 엔드포인트"""

    if user.id != uid_request.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="사용자 ID가 일치하지 않습니다.",
        )
    decoration_user = await DecorationUserService.equip_decoration_user(
        uid_request.uid,
        decoration_ref.did,
        decoration_ref.type,
    )
    if not decoration_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="장식 장착 혹은 해제에 실패했습니다.",
        )

    return decoration_user
