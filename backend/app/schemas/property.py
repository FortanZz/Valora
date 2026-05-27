from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PropertyType(str, Enum):
    """Enum for property types"""
    HOUSE = "house"
    APARTMENT = "apartment"
    OFFICE = "office"
    LAND = "land"


class PropertyCategory(str, Enum):
    """Enum for property categories"""
    RENT = "rent"
    SALE = "sale"


class PropertyCreate(BaseModel):
    """Schema for creating a new property"""
    title: str = Field(..., min_length=5, max_length=200, description="Property title")
    description: Optional[str] = Field(None, max_length=5000, description="Property description")
    location: str = Field(..., min_length=3, max_length=200, description="Property location")
    price: float = Field(..., gt=0, description="Property price")
    property_type: PropertyType = Field(..., description="Type of property")
    category: PropertyCategory = Field(..., description="Category (rent or sale)")
    contact_phone: str = Field(..., min_length=10, max_length=20, description="Contact phone number")
    contact_email: str = Field(..., description="Contact email")
    num_bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms")
    num_bathrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bathrooms")
    area_sqm: Optional[float] = Field(None, gt=0, description="Area in square meters")

    @validator("price")
    def validate_price_range(cls, v):
        """Validate price is in reasonable range"""
        if v > 10_000_000:
            raise ValueError("Price cannot exceed 10,000,000")
        if v < 100:
            raise ValueError("Price must be at least 100")
        return v

    @validator("category", pre=True, always=True)
    def validate_land_rent_constraint(cls, v, values):
        """Enforce business rule: land cannot be rented"""
        if "property_type" in values:
            if values["property_type"] == PropertyType.LAND and v == PropertyCategory.RENT:
                raise ValueError("Land properties cannot be listed for rent, only for sale")
        return v

    @validator("num_bedrooms", "num_bathrooms")
    def validate_rooms_for_land(cls, v, values):
        """Land properties should not have bedrooms/bathrooms"""
        if "property_type" in values:
            if values["property_type"] == PropertyType.LAND and v is not None and v > 0:
                raise ValueError("Land properties should not have bedrooms or bathrooms")
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Beautiful Modern Apartment",
                "description": "Newly built apartment in city center",
                "location": "Downtown, Skopje",
                "price": 150000,
                "property_type": "apartment",
                "category": "sale",
                "contact_phone": "+389701234567",
                "contact_email": "seller@example.com",
                "num_bedrooms": 2,
                "num_bathrooms": 1,
                "area_sqm": 85
            }
        }


class PropertyUpdate(BaseModel):
    """Schema for updating a property"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    location: Optional[str] = Field(None, min_length=3, max_length=200)
    price: Optional[float] = Field(None, gt=0)
    contact_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    contact_email: Optional[str] = Field(None)
    num_bedrooms: Optional[int] = Field(None, ge=0, le=20)
    num_bathrooms: Optional[int] = Field(None, ge=0, le=20)
    area_sqm: Optional[float] = Field(None, gt=0)

    @validator("price")
    def validate_price_range(cls, v):
        """Validate price is in reasonable range"""
        if v is None:
            return v
        if v > 10_000_000:
            raise ValueError("Price cannot exceed 10,000,000")
        if v < 100:
            raise ValueError("Price must be at least 100")
        return v

    class Config:
        schema_extra = {
            "example": {
                "title": "Updated Property Title",
                "price": 180000
            }
        }


class PropertyResponse(BaseModel):
    """Schema for property response"""
    id: int = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    location: str = Field(..., description="Property location")
    price: float = Field(..., description="Property price")
    property_type: PropertyType = Field(..., description="Type of property")
    category: PropertyCategory = Field(..., description="Category (rent or sale)")
    contact_phone: str = Field(..., description="Contact phone number")
    contact_email: str = Field(..., description="Contact email")
    num_bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    num_bathrooms: Optional[int] = Field(None, description="Number of bathrooms")
    area_sqm: Optional[float] = Field(None, description="Area in square meters")
    owner_id: int = Field(..., description="Property owner ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "title": "Beautiful Modern Apartment",
                "description": "Newly built apartment in city center",
                "location": "Downtown, Skopje",
                "price": 150000,
                "property_type": "apartment",
                "category": "sale",
                "contact_phone": "+389701234567",
                "contact_email": "seller@example.com",
                "num_bedrooms": 2,
                "num_bathrooms": 1,
                "area_sqm": 85,
                "owner_id": 1,
                "created_at": "2026-05-28T10:00:00",
                "updated_at": "2026-05-28T10:00:00"
            }
        }


class PropertyListResponse(BaseModel):
    """Schema for property list response"""
    items: List[PropertyResponse] = Field(..., description="List of properties")
    total: int = Field(..., ge=0, description="Total number of properties")
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, description="Items per page")

    class Config:
        schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 10
            }
        }
