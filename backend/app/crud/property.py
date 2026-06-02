from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import PropertyNotFoundException
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate


async def get_property(db: AsyncSession, id: UUID) -> Property:
    result = await db.execute(select(Property).where(Property.id == id))
    db_property = result.scalar_one_or_none()
    if db_property is None:
        raise PropertyNotFoundException()
    return db_property


def _apply_location_search(query, search: str | None):
    if search:
        query = query.where(Property.location.ilike(f"%{search.strip()}%"))
    return query


async def get_properties(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
) -> tuple[list[Property], int]:
    base_query = _apply_location_search(select(Property), search)

    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = total_result.scalar_one()

    result = await db.execute(base_query.offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def create_property(db: AsyncSession, property_in: PropertyCreate) -> Property:
    db_property = Property(**property_in.model_dump())
    db.add(db_property)
    await db.commit()
    await db.refresh(db_property)
    return db_property


async def update_property(
    db: AsyncSession,
    id: UUID,
    property_in: PropertyUpdate,
) -> Property:
    db_property = await get_property(db, id)

    for field, value in property_in.model_dump(exclude_unset=True).items():
        setattr(db_property, field, value)

    await db.commit()
    await db.refresh(db_property)
    return db_property


async def delete_property(db: AsyncSession, id: UUID) -> Property:
    db_property = await get_property(db, id)
    await db.delete(db_property)
    await db.commit()
    return db_property
