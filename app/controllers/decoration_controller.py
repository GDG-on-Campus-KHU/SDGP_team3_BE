from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.core.auth import (
    get_current_active_user,
    get_current_superuser,
    verify_superuser_token,
)
from app.models.decoration_model import (
    Asset,
    AssetType,
    DecorationInDB,
    Landscape,
    LandscapeType,
)
from app.services.decoration_service import DecorationService

router = APIRouter(
    prefix="/api/decorations",  # localhost:80/api/decorations
    tags=["decorations"],
    responses={404: {"description": "Not found"}},
)


# Form 데이터는 따로 Request model을 만들지 않음.
@router.post("/assets/", response_model=Asset, status_code=status.HTTP_201_CREATED)
async def create_asset(
    name: str = Form(...),
    version: int = Form(...),
    type: str = Form(...),
    rarity: int = Form(...),
    color: Optional[str] = Form(...),  # Form은 string으로 변환됨
    file: UploadFile = File(...),
    _: bool = Depends(verify_superuser_token),
) -> Asset:
    """Asset 장식 생성 엔드포인트.
    color는 전달 시, JSON String 형식으로 전달되어야 하며 (ex. {}"trunk": "#FF5733"}),
    DB 혹은 static 디렉토리까지 확인하지 않는 단에서 검증.
    static 디렉토리까지 확인하는 검증은 서비스 레이어에서 처리.
    """
    asset_data = Asset(
        name=name,
        version=version,
        type=type,
        rarity=rarity,
        color=color,
    )

    # 타입 검사
    try:
        type_enum = AssetType(type)
    except ValueError:
        print(f"Invalid asset type: {type}")
        allowed_types = [member.value for member in AssetType]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset 타입에 맞지 않습니다. 허용되는 타입: {', '.join(allowed_types)}",
        )

    # 파일 확장자 검사
    file_extension = file.filename.split(".")[-1]
    allowed_extensions = ["png", "jpg", "jpeg", "svg"]

    if file_extension not in allowed_extensions:
        print(f"Invalid file type: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    try:
        asset = await DecorationService.create_asset(asset_data, file)
        print(f"COMPLETED: asset: {asset}")
        if not asset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="장식 생성에 실패했습니다.",
            )
        return asset
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Form 데이터는 따로 Request model을 만들지 않음.
@router.post(
    "/landscapes/",
    response_model=Landscape,
    status_code=status.HTTP_201_CREATED,
)
async def create_landscape(
    name: str = Form(...),
    version: int = Form(...),
    type: str = Form(...),
    rarity: int = Form(...),
    file: UploadFile = File(...),
    _: bool = Depends(verify_superuser_token),
) -> Landscape:
    """Landscape 장식 생성 엔드포인트.
    DB 혹은 static 디렉토리까지 확인하지 않는 단에서 검증.
    static 디렉토리까지 확인하는 검증은 서비스 레이어에서 처리.
    """
    landscape_data = Landscape(
        name=name,
        version=version,
        type=type,
        rarity=rarity,
    )
    # 타입 검사
    try:
        landscape_data.type = LandscapeType[type]
    except KeyError:
        print(f"Invalid landscape type: {type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Landscape 타입에 맞지 않습니다. 허용되는 타입: {', '.join(LandscapeType.__members__.keys())}",
        )

    # 파일 확장자 검사
    file_extension = file.filename.split(".")[-1]
    allowed_extensions = ["png", "jpg", "jpeg", "svg"]

    # TODO: 이후 용량 검사 (Ddos 공격 방지)
    if file_extension not in allowed_extensions:
        print(f"Invalid file type: {file_extension}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types are: {', '.join(allowed_extensions)}",
        )

    try:
        landscape = await DecorationService.create_landscape(landscape_data, file)
        print(f"COMPLETED: landscape: {landscape}")
        if not landscape:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="장식 생성에 실패했습니다.",
            )

        return landscape
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[DecorationInDB])
async def get_all_decorations(
    _: bool = Depends(verify_superuser_token),
) -> List[DecorationInDB]:
    """모든 장식 조회 엔드포인트"""
    return await DecorationService.get_all_decorations()


# 임시로 fastapi에서 제공하는 static file을 사용. 이후에는 nginx 등에서 제공할 예정.
@router.get("/{type}/{version}/{name}", response_class=FileResponse)
async def get_decoration_file(
    type: str,
    version: int,
    name: str,
) -> FileResponse:
    """장식 파일 조회 엔드포인트"""
    # 경로 조작 위험성: FastAPI에서 제공하는 static file을 mounting하여 사용해서 OK.
    # TODO: 악의적인 파일명, MIME 타입 조작 방지도...
    # static file에서 조회
    is_exist, decoration_file_path = (
        await DecorationService._check_decoration_file_path(name, version, type)
    )  # "static/{type}/{version}/{name}"
    if not is_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="장식 파일을 찾을 수 없습니다.",
        )

    return FileResponse(decoration_file_path)
