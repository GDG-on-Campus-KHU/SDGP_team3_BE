# decoration_model.py
import enum
import json
import re
from datetime import datetime, timezone
from typing import Any, NewType, Optional, Union

from pydantic import BaseModel, EmailStr, Field, field_validator

HEX_COLOR_PATTERN = re.compile(r"^#[A-Fa-f0-9]{6}$")


# Landscape 타입 (각 서브타입별로 하나씩만 장착 가능)
class LandscapeType(str, enum.Enum):
    TERRAIN = "terrain"
    SKY = "sky"


# Asset 타입 (여러 개 장착 가능)
class AssetType(str, enum.Enum):
    GRASS = "grass"
    TREE = "tree"
    FLOWER = "flower"
    ANIMAL = "animal"


class DecorationType(str, enum.Enum):
    """Landscape 타입과 Asset 타입을 모두 포함하는 Enum 클래스"""

    TERRAIN = "terrain"
    SKY = "sky"
    GRASS = "grass"
    TREE = "tree"
    FLOWER = "flower"
    ANIMAL = "animal"


class DecorationBase(BaseModel):
    """DecorationBase 기본 정보 모델"""

    name: str = Field(..., max_length=50, description="장식 이름")
    version: int = Field(..., description="장식 버전")
    type: str = Field(..., description="장식 타입")
    rarity: int = Field(..., description="장식 희귀도")

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class DecorationResponse(DecorationBase):
    """Decoration 장식 Response 모델"""

    color: Optional[str] = Field(
        ...,
        description="JSON String. value는 장식 색상임(Asset 타입에만 해당. 16진수 3개 RGB 값으로만.)",
    )


class DecorationReference(BaseModel):
    """
    Decoration의 참조를 위한 최소 정보 모델
    ID와 타입만 포함하는 경량화된 모델
    """

    did: int = Field(..., description="장식 ID")
    type: DecorationType = Field(..., description="장식 타입")


class Decoration(DecorationBase):
    """Decoration 장식 모델"""

    pass

    did: int = Field(..., description="장식 ID")
    type: DecorationType = Field(..., description="장식 타입")


class LandscapeBase(DecorationBase):
    """LandscapeBase 장식 모델"""

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class Landscape(LandscapeBase):
    pass


class CreateLandscapeResponse(LandscapeBase):
    """Landscape 장식 생성 응답 모델"""

    pass


class Terrain(LandscapeBase):
    """Terrain 장식 모델"""

    type: LandscapeType = LandscapeType.TERRAIN


class Sky(LandscapeBase):
    """Sky 장식 모델"""

    type: LandscapeType = LandscapeType.SKY


class AssetBase(DecorationBase):
    """Asset 장식 추상 모델"""

    color: Optional[str] = Field(
        ..., description="장식 색상 (Asset 타입에만 해당. 16진수 3개 RGB 값으로만.)"
    )

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}

    @field_validator("color")
    @classmethod
    def validate_color(cls: Any, value: Any) -> Any:
        if value is None:
            return value

        try:
            value_dict = json.loads(value)
        except json.JSONDecodeError:
            raise ValueError("Color must be a JSON String.")

        for key, val in value_dict.items():
            if not HEX_COLOR_PATTERN.match(val):
                raise ValueError(
                    f'Invalid color code format at {key}: {val}. Use hex format (e.g., "#FF5733").'
                )
        return value


class CreateAssetResponse(AssetBase):
    """Asset 장식 생성 응답 모델"""

    pass


class Asset(AssetBase):
    pass


class AssetDict(DecorationBase):
    """
    Asset 장식 모델.
    내부적으로 사용할 수 있기에
    - "color"는 dict 형태로 변환하여 사용.

    """

    color: Optional[dict] = Field(..., description="dictionary 변환 형태로만 사용")


class Grass(AssetBase):
    """Grass 장식 모델"""

    type: AssetType = AssetType.GRASS


class Tree(AssetBase):
    """Tree 장식 모델"""

    type: AssetType = AssetType.TREE


class Flower(AssetBase):
    """Flower 장식 모델"""

    type: AssetType = AssetType.FLOWER


class Animal(AssetBase):
    """Animal 장식 모델"""

    type: AssetType = AssetType.ANIMAL


class DecorationInDB(BaseModel):
    """Decoration 데이터베이스 모델"""

    # from_orm 사용
    class Config:
        orm_mode = True  # from_orm 메서드 활성화 및 ORM

    id: int
    name: str
    version: int
    rarity: int
    type: DecorationType
    color: Optional[str]  # Asset 타입에만 해당
