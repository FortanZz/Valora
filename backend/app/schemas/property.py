from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    OFFICE = "office"
    LAND = "land"


class PropertyCategory(str, Enum):
    SALE = "sale"
    RENT = "rent"


class PropertyBase(BaseModel):
    title: str = Field(..., min_length=4, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    location: str = Field(..., min_length=2, max_length=160)
    price: float = Field(..., ge=100, le=50_000_000)
    property_type: PropertyType
    category: PropertyCategory
    contact_phone: str = Field(..., min_length=6, max_length=40)
    contact_email: EmailStr
    num_bedrooms: Optional[int] = Field(default=None, ge=0, le=50)
    num_bathrooms: Optional[int] = Field(default=None, ge=0, le=50)
    area_sqm: Optional[float] = Field(default=None, gt=0, le=1_000_000)

    @model_validator(mode="after")
    def validate_property_rules(self):
        if self.property_type == PropertyType.LAND:
            if self.category == PropertyCategory.RENT:
                raise ValueError("Land properties cannot be rented")
            if self.num_bedrooms not in (None, 0):
                raise ValueError("Land properties should not include bedrooms")
            if self.num_bathrooms not in (None, 0):
                raise ValueError("Land properties should not include bathrooms")
        return self


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=4, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    location: Optional[str] = Field(default=None, min_length=2, max_length=160)
    price: Optional[float] = Field(default=None, ge=100, le=50_000_000)
    contact_phone: Optional[str] = Field(default=None, min_length=6, max_length=40)
    contact_email: Optional[EmailStr] = None
    num_bedrooms: Optional[int] = Field(default=None, ge=0, le=50)
    num_bathrooms: Optional[int] = Field(default=None, ge=0, le=50)
    area_sqm: Optional[float] = Field(default=None, gt=0, le=1_000_000)


class PropertyResponse(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
