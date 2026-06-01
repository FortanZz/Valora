from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import property as property_crud
from app.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate
from app.session import get_db

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=List[PropertyResponse])
async def list_properties(
    db: DbSession,
    skip: int = 0,
    limit: int = 100,
) -> List[PropertyResponse]:
    return await property_crud.get_properties(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=PropertyResponse)
async def get_property(db: DbSession, id: UUID) -> PropertyResponse:
    property_obj = await property_crud.get_property(db, id)
    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_obj


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    db: DbSession,
    property_in: PropertyCreate,
) -> PropertyResponse:
    return await property_crud.create_property(db, property_in)


@router.put("/{id}", response_model=PropertyResponse)
async def update_property(
    db: DbSession,
    id: UUID,
    property_in: PropertyUpdate,
) -> PropertyResponse:
    property_obj = await property_crud.update_property(db, id, property_in)
    if property_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
    return property_obj


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(db: DbSession, id: UUID) -> None:
    deleted = await property_crud.delete_property(db, id)
    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Property not found",
        )
