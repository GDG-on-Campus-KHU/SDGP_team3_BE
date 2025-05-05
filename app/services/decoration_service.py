import glob
import os
from typing import List, Optional, Tuple

from fastapi import UploadFile

from app.models.decoration_model import Asset, DecorationInDB, Landscape
from app.repositories.decoration_repository import DecorationRepository


class DecorationService:
    """DecorationService는 장식 관련 비즈니스 로직을 처리하는 서비스입니다."""

    @staticmethod
    # 파일 저장 경로 중복 체크. TODO: 이후 파일 관련 로직은 infrastructure 레이어에서 처리.
    # {type}/{version}/{name}
    async def _check_decoration_file_path(
        name: str,
        version: int,
        type: str,
        filename: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        파일 존재 경로 체크 메서드
        filename 존재 시 (생성 시 체크용), filename을 사용하여 저장 경로를 생성하고,
        filename이 존재하지 않을 시 (순수 체크용), name을 사용하여 저장 경로를 생성합니다.
        """
        # 파일 저장 경로 중복 체크
        base_path = os.path.join("static", type, str(version))
        if filename:  # 저장 시.
            extension = filename.split(".")[-1]
            filename = name + "." + extension  # 파일명 변경
            file_path = os.path.join(base_path, filename)
        else:  # 조회 시.
            # 확장자 없는 파일명으로 찾기
            # glob을 사용하여 확장자 없는 파일명으로 찾기
            file_pattern = os.path.join(base_path, name + ".*")
            # glob을 사용하여 확장자 없는 파일명으로 찾기
            file_list = glob.glob(file_pattern)
            if file_list:
                file_path = file_list[0]
            else:
                file_path = os.path.join(base_path, name)  # 확장자 없는 파일명으로 찾기
        print(f"file_path: {file_path}")

        if os.path.exists(file_path):
            return True, file_path
        else:
            # 디렉토리 생성
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # 파일이 존재하지 않으면 False 반환
            return False, file_path

    @staticmethod
    async def create_asset(asset_data: Asset, file: UploadFile) -> Optional[Asset]:
        """Asset 장식 생성 메서드"""

        # Asset 파일 저장 경로 중복 체크
        # {type}/{version}/{name}
        is_exist, asset_path = await DecorationService._check_decoration_file_path(
            asset_data.name,
            asset_data.version,
            asset_data.type,
            file.filename,
        )

        if is_exist:
            raise ValueError("이미 존재하는 Asset 파일입니다.")
        try:
            # 데이터베이스에 Asset 장식 생성 (먼저 체크하기 때문에 파일 쓰기 중복 문제 방지 가능)
            asset = await DecorationRepository.create_asset(asset_data)
        except ValueError as e:
            raise ValueError(f"Asset 생성 실패: {str(e)}")

        try:
            # 파일 저장
            with open(asset_path, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise ValueError(f"파일 저장 실패: {str(e)}")

        # print("asset 성공", asset)
        # 모두 성공하면 Asset 반환
        return asset

    @staticmethod
    async def create_landscape(
        landscape_data: Landscape, file: UploadFile
    ) -> Optional[Landscape]:
        """Landscape 장식 생성 메서드"""

        is_exist, landscape_path = await DecorationService._check_decoration_file_path(
            landscape_data.name,
            landscape_data.version,
            landscape_data.type,
            file.filename,
        )
        if is_exist:
            raise ValueError("이미 존재하는 Landscape 파일입니다.")
        try:
            # 데이터베이스에 Landscape 장식 생성
            landscape = await DecorationRepository.create_landscape(landscape_data)
        except ValueError as e:
            raise ValueError(f"Landscape 생성 실패: {str(e)}")
        try:
            # 파일 저장
            with open(landscape_path, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise ValueError(f"파일 저장 실패: {str(e)}")
        # 모두 성공하면 Landscape 반환
        return landscape

    @staticmethod
    async def get_all_decorations() -> List[DecorationInDB]:
        """모든 장식 조회 메서드"""
        try:
            decorations = await DecorationRepository.get_all_decorations()
            filtered_decorations: List[DecorationInDB] = [
                decoration for decoration in decorations if decoration is not None
            ]
            return filtered_decorations
        except Exception as e:
            raise ValueError(f"장식 조회 실패: {str(e)}")
