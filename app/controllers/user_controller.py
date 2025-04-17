from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.models.user_model import User, UserCreate, UserLogin, UserUpdate
from app.services.user_service import UserService

# OAuth2 인증 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

# 라우터 설정
router = APIRouter(
    prefix="/api/users",  # localhost:80/api/users
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


# 현재 사용자 가져오기 의존성
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """JWT 토큰에서 현재 사용자 정보 가져오기"""
    user = await UserService.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# 활성 사용자인지 확인하는 의존성
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """현재 사용자가 활성 상태인지 확인"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="비활성화된 사용자"
        )
    return current_user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate) -> Optional[User]:
    """사용자 생성 엔드포인트"""
    try:
        user = await UserService.create_user(user_data)

        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[User])
async def get_all_users(
    current_user: User = Depends(get_current_active_user),
) -> List[User]:
    """모든 사용자 조회 엔드포인트"""
    print(f"current user: {current_user}")
    return await UserService.get_all_users()


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """현재 로그인한 사용자 정보 조회"""
    return current_user


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: int, current_user: User = Depends(get_current_active_user)
) -> Optional[User]:
    # =Depends(get_current_active_user)
    """ID로 사용자 조회 엔드포인트"""
    user = await UserService.get_user_by_id(user_id)
    print(f"current user: {current_user}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다.",
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Optional[User]:
    """사용자 정보 업데이트 엔드포인트"""
    # 자신의 정보만 업데이트 가능 (관리자 제외)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 정보를 수정할 권한이 없습니다.",
        )

    try:
        user = await UserService.update_user(user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다.",
            )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, current_user: User = Depends(get_current_active_user)
) -> None:
    """사용자 삭제 엔드포인트"""
    # 자신의 계정만 삭제 가능 (관리자 제외)
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자를 삭제할 권한이 없습니다.",
        )

    success = await UserService.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다.",
        )


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Optional[dict]:
    """OAuth2 호환 토큰 엔드포인트"""
    user_login = UserLogin(email=form_data.username, password=form_data.password)
    auth_result = await UserService.authenticate_user(user_login)

    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": auth_result["access_token"],
        "token_type": auth_result["token_type"],
    }


@router.post("/login", response_model=User)
async def login(user_data: UserLogin) -> Union[User, Any]:
    """사용자 로그인 엔드포인트"""
    auth_result = await UserService.authenticate_user(user_data)

    if not auth_result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다.",
        )

    return auth_result["user"]


from app.models.user_model import Challenge, Decoration


@router.get("/{user_id}/challenges", response_model=List[Challenge])
async def get_fake_challenges_by_id(user_id: int) -> Optional[List[Any]]:
    """ID로 사용자의 챌린지 조회 엔드포인트"""
    challenges = await UserService.get_fake_challenges_by_id(user_id)
    if not challenges:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다.",
        )
    return challenges


@router.get("/{user_id}/decorations", response_model=List[Decoration])
async def get_fake_decorations_by_id(user_id: int) -> Optional[List[Any]]:
    """ID로 사용자의 장식 조회 엔드포인트"""
    decorations = await UserService.get_fake_decorations_by_id(user_id)
    if not decorations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID가 {user_id}인 사용자를 찾을 수 없습니다.",
        )
    return decorations
