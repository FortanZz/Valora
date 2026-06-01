from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.models import Property  # noqa: F401
from app.models.base import Base

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.debug)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_async_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
