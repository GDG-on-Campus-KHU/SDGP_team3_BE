import enum
import re
from datetime import datetime, timedelta, timezone
from typing import Any, List, NewType, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.stamp_model import StampInDB


class ChallengeStampInDB(BaseModel):
    """ChallengeStamp 챌린지 스탬프 모델"""

    cid: int = Field(..., description="챌린지 ID")
    sid: int = Field(..., description="스탬프 ID")
