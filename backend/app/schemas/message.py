from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageCreate(BaseModel):
    property_id: int = Field(..., gt=0)
    body: str = Field(..., min_length=1, max_length=2000)

    @field_validator("body")
    @classmethod
    def validate_body(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message body is required")
        return stripped


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender_id: int
    recipient_id: int
    property_id: Optional[int] = None
    body: str
    created_at: datetime
    read_at: Optional[datetime] = None
