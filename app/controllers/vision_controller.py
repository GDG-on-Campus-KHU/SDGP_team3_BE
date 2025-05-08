from fastapi import HTTPException, status, APIRouter, UploadFile, File
import shutil
import uuid
import os
from typing import Literal
from app.services.vision_service import detect_spoon_fork_from_image, detect_tumbler_in_image


# vision 관련 라우터
router = APIRouter(
    prefix="/api/vision",
    tags=["vision"],
    responses={404: {"description": "Not found"}},
)

@router.post("/spoon-fork", summary="수저/포크 OX 판별", response_model=dict)
async def analyze_spoon_fork(file: UploadFile = File(...)) -> dict[str, Literal["O", "X"]]:
    """OCR로 '수저, 포크 O/X' 인식 결과 반환"""
    temp_file_name = f"temp_{uuid.uuid4().hex}.png"
    try:
        with open(temp_file_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detect_spoon_fork_from_image(temp_file_name)
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)


@router.post("/tumbler", summary="텀블러 객체 탐지", response_model=dict)
async def detect_tumbler(file: UploadFile = File(...)) -> dict[str, Literal["Tumbler", "Not Tumbler"]]:
    """Cloud Vision의 Label Detection으로 텀블러 객체 존재 여부 반환"""
    temp_file_name = f"temp_{uuid.uuid4().hex}.png"
    try:
        with open(temp_file_name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = detect_tumbler_in_image(temp_file_name)
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    finally:
        if os.path.exists(temp_file_name):
            os.remove(temp_file_name)



