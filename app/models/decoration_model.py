import enum
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

    id: int
    name: str = Field(..., max_length=50, description="장식 이름")
    version: str = Field(..., max_length=10, description="장식 버전")
    # acquired_at: datetime = Field(
    #     default_factory=datetime.now(timezone.utc), description="획득 날짜"
    # )
    type: str = Field(..., description="장식 타입")
    rairity: int = Field(..., description="장식 희귀도")


class Decoration(DecorationBase):
    """Decoration 장식 모델"""

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}

    pass


class Landscape(DecorationBase):
    """Landscape 장식 모델"""

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}


class Terrain(Landscape):
    """Terrain 장식 모델"""

    type: LandscapeType = LandscapeType.TERRAIN


class Sky(Landscape):
    """Sky 장식 모델"""

    type: LandscapeType = LandscapeType.SKY


class Asset(DecorationBase):
    """Asset 장식 모델"""

    color: str  # 색상 코드 (예: "#FF5733")

    class Config:
        # Pydantic v2에서는 이 설정을 통해 추상 모델임을 나타낼 수 있음
        model_config = {"extra": "allow"}

    @field_validator("color")
    @classmethod
    def validate_color(cls: Any, value: Any) -> Any:
        if not HEX_COLOR_PATTERN.match(value):
            raise ValueError(
                'Invalid color code format. Use hex format (e.g., "#FF5733").'
            )
        return value


class Grass(Asset):
    """Grass 장식 모델"""

    type: AssetType = AssetType.GRASS


class Tree(Asset):
    """Tree 장식 모델"""

    type: AssetType = AssetType.TREE
    pass


class Flower(Asset):
    """Flower 장식 모델"""

    type: AssetType = AssetType.FLOWER
    pass


class Animal(Asset):
    """Animal 장식 모델"""

    type: AssetType = AssetType.ANIMAL
    pass


class DecorationInDB(BaseModel):
    """Decoration 데이터베이스 모델"""

    # from_orm 사용
    class Config:
        orm_mode = True  # from_orm 메서드 활성화 및 ORM

    id: int
    name: str
    version: str
    rairity: int
    type: DecorationType
