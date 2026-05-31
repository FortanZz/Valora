from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user_id
from app.database import (
    create_property as create_property_record,
    delete_property as delete_property_record,
    get_property_by_id,
    get_user_by_id,
    search_properties as search_properties_db,
    update_property as update_property_record,
)
from app.schemas.property import (
    PropertyCategory,
    PropertyCreate,
    PropertyResponse,
    PropertyUpdate,
    PropertyType,
)

router = APIRouter()


def _get_property_or_404(property_id: int) -> dict:
    property_item = get_property_by_id(property_id)
    if not property_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_item


def _verify_owner(property_item: dict, user_id: int) -> None:
    if property_item["owner_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this property",
        )


def _validate_user_exists(user_id: int) -> None:
    if get_user_by_id(user_id) is None:
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
    created_at = datetime.utcnow()
    property_data = create_property_record(
        owner_id=current_user_id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        price=payload.price,
        property_type=payload.property_type.value,
        category=payload.category.value,
        contact_phone=payload.contact_phone,
        contact_email=payload.contact_email,
        num_bedrooms=payload.num_bedrooms,
        num_bathrooms=payload.num_bathrooms,
        area_sqm=payload.area_sqm,
        created_at=created_at,
        updated_at=created_at,
    )
    return PropertyResponse(**property_data)


@router.get("/", response_model=List[PropertyResponse])
def list_properties(
    skip: int = 0,
    limit: int = 20,
) -> List[PropertyResponse]:
    return [PropertyResponse(**item) for item in search_properties_db(skip=skip, limit=limit)]


@router.get("/search", response_model=List[PropertyResponse])
def search_properties_endpoint(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[PropertyType] = None,
    category: Optional[PropertyCategory] = None,
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "newest",
) -> List[PropertyResponse]:
    results = search_properties_db(
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type.value if property_type else None,
        category=category.value if category else None,
        location=location,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
    )
    return [PropertyResponse(**item) for item in results]


@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(property_id: int) -> PropertyResponse:
    stored_property = _get_property_or_404(property_id)
    return PropertyResponse(**stored_property)


@router.put("/{property_id}", response_model=PropertyResponse)
def update_property(
    property_id: int,
    payload: PropertyUpdate,
    current_user_id: int = Depends(get_current_user_id),
) -> PropertyResponse:
    _validate_user_exists(current_user_id)
    stored_property = _get_property_or_404(property_id)
    _verify_owner(stored_property, current_user_id)

    if stored_property["property_type"] == PropertyType.LAND.value:
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

    updates = payload.model_dump(exclude_unset=True)
    if stored_property["property_type"] == PropertyType.LAND.value:
        if updates.get("num_bedrooms") is not None and updates["num_bedrooms"] > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land properties should not include bedrooms",
            )
        if updates.get("num_bathrooms") is not None and updates["num_bathrooms"] > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Land properties should not include bathrooms",
            )

    updated_property = update_property_record(
        property_id,
        updates=updates,
        updated_at=datetime.utcnow(),
    )
    return PropertyResponse(**updated_property)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(
    property_id: int,
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    _validate_user_exists(current_user_id)
    stored_property = _get_property_or_404(property_id)
    _verify_owner(stored_property, current_user_id)
    delete_property_record(property_id)
