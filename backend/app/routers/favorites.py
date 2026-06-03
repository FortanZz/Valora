from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user_id
from app.database import (
    favorite_property,
    get_favorite_properties,
    get_property_by_id,
    get_user_by_id,
    remove_favorite,
)
from app.schemas.favorite import FavoriteResponse
from app.schemas.property import PropertyResponse

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


def _validate_user_exists(user_id: int) -> None:
    if get_user_by_id(user_id) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _validate_property_exists(property_id: int) -> None:
    if get_property_by_id(property_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )


@router.post("/{property_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_favorite(
    property_id: int,
    current_user_id: int = Depends(get_current_user_id),
) -> FavoriteResponse:
    _validate_user_exists(current_user_id)
    _validate_property_exists(property_id)
    favorite = favorite_property(
        user_id=current_user_id,
        property_id=property_id,
        created_at=datetime.utcnow(),
    )
    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return FavoriteResponse(**favorite)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_favorite(
    property_id: int,
    current_user_id: int = Depends(get_current_user_id),
) -> None:
    _validate_user_exists(current_user_id)
    _validate_property_exists(property_id)
    remove_favorite(current_user_id, property_id)


@router.get("/", response_model=List[PropertyResponse])
def list_favorites(
    current_user_id: int = Depends(get_current_user_id),
) -> List[PropertyResponse]:
    _validate_user_exists(current_user_id)
    return [
        PropertyResponse(**property_item)
        for property_item in get_favorite_properties(current_user_id)
    ]
