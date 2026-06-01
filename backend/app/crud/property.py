from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate


async def get_property(db: AsyncSession, id: UUID) -> Property | None:
    result = await db.execute(select(Property).where(Property.id == id))
    return result.scalar_one_or_none()


async def get_properties(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Property]:
    result = await db.execute(select(Property).offset(skip).limit(limit))
    return list(result.scalars().all())


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
) -> Property | None:
    db_property = await get_property(db, id)
    if db_property is None:
        return None

    for field, value in property_in.model_dump(exclude_unset=True).items():
        setattr(db_property, field, value)

    await db.commit()
    await db.refresh(db_property)
    return db_property


async def delete_property(db: AsyncSession, id: UUID) -> Property | None:
    db_property = await get_property(db, id)
    if db_property is None:
        return None

    await db.delete(db_property)
    await db.commit()
    return db_property
