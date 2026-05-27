from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user_id
from app.routers.auth import USERS_BY_ID
from app.schemas.property import (
    PropertyCategory,
    PropertyCreate,
    PropertyResponse,
    PropertyUpdate,
    PropertyType,
)

router = APIRouter()


@dataclass
class StoredProperty:
    id: int
    owner_id: int
    title: str
    description: Optional[str]
    location: str
    price: float
    property_type: PropertyType
    category: PropertyCategory
    contact_phone: str
    contact_email: str
    num_bedrooms: Optional[int]
    num_bathrooms: Optional[int]
    area_sqm: Optional[float]
    created_at: datetime
    updated_at: datetime


PROPERTIES_BY_ID: Dict[int, StoredProperty] = {}
NEXT_PROPERTY_ID = 1


def _next_property_id() -> int:
    global NEXT_PROPERTY_ID
    result = NEXT_PROPERTY_ID
    NEXT_PROPERTY_ID += 1
    return result


def _get_property_or_404(property_id: int) -> StoredProperty:
    property_item = PROPERTIES_BY_ID.get(property_id)
    if not property_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_item


def _verify_owner(property_item: StoredProperty, user_id: int) -> None:
    if property_item.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this property",
        )


def _validate_user_exists(user_id: int) -> None:
    if user_id not in USERS_BY_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    current_user_id: int = Depends(get_current_user_id),
) -> PropertyResponse:
    _validate_user_exists(current_user_id)
    property_id = _next_property_id()
    created_at = datetime.utcnow()

    stored_property = StoredProperty(
        id=property_id,
        owner_id=current_user_id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        price=payload.price,
        property_type=payload.property_type,
        category=payload.category,
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        num_bedrooms=payload.num_bedrooms,
        num_bathrooms=payload.num_bathrooms,
        area_sqm=payload.area_sqm,
        created_at=created_at,
        updated_at=created_at,
    )
    PROPERTIES_BY_ID[property_id] = stored_property
    return PropertyResponse.from_orm(stored_property)


@router.get("/", response_model=List[PropertyResponse])
def list_properties(
    skip: int = 0,
    limit: int = 20,
) -> List[PropertyResponse]:
    items = list(PROPERTIES_BY_ID.values())[skip : skip + limit]
    return [PropertyResponse.from_orm(item) for item in items]


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int) -> PropertyResponse:
    stored_property = _get_property_or_404(property_id)
    return PropertyResponse.from_orm(stored_property)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    current_user_id: int = Depends(get_current_user_id),
) -> PropertyResponse:
    _validate_user_exists(current_user_id)
    stored_property = _get_property_or_404(property_id)
    _verify_owner(stored_property, current_user_id)

    if stored_property.property_type == PropertyType.LAND:
        if payload.num_bedrooms is not None and payload.num_bedrooms > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land properties should not include bedrooms",
            )
        if payload.num_bathrooms is not None and payload.num_bathrooms > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land properties should not include bathrooms",
            )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(stored_property, field, value)

    stored_property.updated_at = datetime.utcnow()
    return PropertyResponse.from_orm(stored_property)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    _validate_user_exists(current_user_id)
    stored_property = _get_property_or_404(property_id)
    _verify_owner(stored_property, current_user_id)

    del PROPERTIES_BY_ID[property_id]
