import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    event,
    func,
    or_,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

DB_PATH = os.getenv("VALORA_DB_PATH") or str(Path(__file__).parent.parent / "valora.db")
ENGINE: Optional[Engine] = None
SessionLocal: Optional[sessionmaker[Session]] = None


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    properties: Mapped[list["PropertyRecord"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class PropertyRecord(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    property_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    contact_phone: Mapped[str] = mapped_column(String(40), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    num_bedrooms: Mapped[Optional[int]] = mapped_column(Integer)
    num_bathrooms: Mapped[Optional[int]] = mapped_column(Integer)
    area_sqm: Mapped[Optional[float]] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    owner: Mapped[UserRecord] = relationship(back_populates="properties")


def _database_url(path: str) -> tuple[str, Dict[str, Any]]:
    if path == ":memory:":
        return "sqlite://", {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

    connect_args: Dict[str, Any] = {"check_same_thread": False}
    if path.startswith("file:"):
        connect_args["uri"] = True
        return f"sqlite:///{path}", {"connect_args": connect_args}

    return f"sqlite:///{path}", {"connect_args": connect_args}


def _ensure_engine() -> Engine:
    global ENGINE, SessionLocal
    if ENGINE is None:
        url, options = _database_url(DB_PATH)
        ENGINE = create_engine(url, future=True, **options)

        @event.listens_for(ENGINE, "connect")
        def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.close()

        SessionLocal = sessionmaker(ENGINE, expire_on_commit=False, future=True)
        Base.metadata.create_all(ENGINE)
    return ENGINE


def init_db(path: Optional[str] = None) -> Engine:
    global DB_PATH, ENGINE, SessionLocal
    if path:
        DB_PATH = path
    if ENGINE is not None:
        ENGINE.dispose()
        ENGINE = None
        SessionLocal = None
    return _ensure_engine()


def close_db() -> None:
    global ENGINE, SessionLocal
    if ENGINE is not None:
        ENGINE.dispose()
        ENGINE = None
        SessionLocal = None


@contextmanager
def _session_scope() -> Iterator[Session]:
    _ensure_engine()
    if SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized")
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyIntegrityError as exc:
        session.rollback()
        if isinstance(exc.orig, sqlite3.IntegrityError):
            raise exc.orig from exc
        raise
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _row_to_user(row: Optional[UserRecord]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row.id,
        "email": row.email,
        "first_name": row.first_name,
        "last_name": row.last_name,
        "hashed_password": row.hashed_password,
        "created_at": row.created_at,
    }


def _row_to_property(row: Optional[PropertyRecord]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row.id,
        "owner_id": row.owner_id,
        "title": row.title,
        "description": row.description,
        "location": row.location,
        "price": row.price,
        "property_type": row.property_type,
        "category": row.category,
        "contact_phone": row.contact_phone,
        "contact_email": row.contact_email,
        "num_bedrooms": row.num_bedrooms,
        "num_bathrooms": row.num_bathrooms,
        "area_sqm": row.area_sqm,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def create_user(
    email: str,
    first_name: str,
    last_name: str,
    hashed_password: str,
    created_at: datetime,
) -> Dict[str, Any]:
    with _session_scope() as session:
        user = UserRecord(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
            created_at=created_at,
        )
        session.add(user)
        session.flush()
        return _row_to_user(user) or {}


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        row = session.execute(
            select(UserRecord).where(UserRecord.email == email)
        ).scalar_one_or_none()
        return _row_to_user(row)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        row = session.get(UserRecord, user_id)
        return _row_to_user(row)


def create_property(
    owner_id: int,
    title: str,
    description: Optional[str],
    location: str,
    price: float,
    property_type: str,
    category: str,
    contact_phone: str,
    contact_email: str,
    num_bedrooms: Optional[int],
    num_bathrooms: Optional[int],
    area_sqm: Optional[float],
    created_at: datetime,
    updated_at: datetime,
) -> Dict[str, Any]:
    with _session_scope() as session:
        property_item = PropertyRecord(
            owner_id=owner_id,
            title=title,
            description=description,
            location=location,
            price=price,
            property_type=property_type,
            category=category,
            contact_phone=contact_phone,
            contact_email=contact_email,
            num_bedrooms=num_bedrooms,
            num_bathrooms=num_bathrooms,
            area_sqm=area_sqm,
            created_at=created_at,
            updated_at=updated_at,
        )
        session.add(property_item)
        session.flush()
        return _row_to_property(property_item) or {}


def get_property_by_id(property_id: int) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        return _row_to_property(session.get(PropertyRecord, property_id))


def get_properties_by_owner(owner_id: int) -> List[Dict[str, Any]]:
    with _session_scope() as session:
        rows = session.execute(
            select(PropertyRecord)
            .where(PropertyRecord.owner_id == owner_id)
            .order_by(PropertyRecord.created_at.desc(), PropertyRecord.id.desc())
        ).scalars()
        return [item for row in rows if (item := _row_to_property(row)) is not None]


def update_property(
    property_id: int,
    updates: Dict[str, Any],
    updated_at: datetime,
) -> Optional[Dict[str, Any]]:
    allowed_fields = {
        "title",
        "description",
        "location",
        "price",
        "contact_phone",
        "contact_email",
        "num_bedrooms",
        "num_bathrooms",
        "area_sqm",
    }
    with _session_scope() as session:
        property_item = session.get(PropertyRecord, property_id)
        if property_item is None:
            return None
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(property_item, key, value)
        property_item.updated_at = updated_at
        session.flush()
        return _row_to_property(property_item)


def delete_property(property_id: int) -> None:
    with _session_scope() as session:
        property_item = session.get(PropertyRecord, property_id)
        if property_item is not None:
            session.delete(property_item)


def _property_search_clauses(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
) -> tuple[List[Any], List[Any]]:
    clauses: List[Any] = []

    if search:
        clauses.append(func.lower(PropertyRecord.location).like(f"%{search.strip().lower()}%"))

    if query:
        like_query = f"%{query.strip().lower()}%"
        clauses.append(
            or_(
                func.lower(PropertyRecord.title).like(like_query),
                func.lower(PropertyRecord.description).like(like_query),
                func.lower(PropertyRecord.location).like(like_query),
            )
        )
    if min_price is not None:
        clauses.append(PropertyRecord.price >= min_price)
    if max_price is not None:
        clauses.append(PropertyRecord.price <= max_price)
    if property_type:
        clauses.append(PropertyRecord.property_type == property_type)
    if category:
        clauses.append(PropertyRecord.category == category)
    if location:
        clauses.append(func.lower(PropertyRecord.location).like(f"%{location.strip().lower()}%"))

    return clauses, []


def count_properties(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
) -> int:
    clauses, _params = _property_search_clauses(
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        category=category,
        location=location,
        search=search,
    )
    with _session_scope() as session:
        statement = select(func.count()).select_from(PropertyRecord)
        if clauses:
            statement = statement.where(*clauses)
        row = session.execute(statement).scalar_one()
        return int(row)


def search_properties(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    property_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    sort_by: str = "newest",
) -> List[Dict[str, Any]]:
    clauses, _params = _property_search_clauses(
        query=query,
        min_price=min_price,
        max_price=max_price,
        property_type=property_type,
        category=category,
        location=location,
        search=search,
    )
    statement = select(PropertyRecord)
    if clauses:
        statement = statement.where(*clauses)

    if sort_by == "price-asc":
        statement = statement.order_by(PropertyRecord.price.asc(), PropertyRecord.created_at.desc())
    elif sort_by == "price-desc":
        statement = statement.order_by(PropertyRecord.price.desc(), PropertyRecord.created_at.desc())
    else:
        statement = statement.order_by(PropertyRecord.created_at.desc(), PropertyRecord.id.desc())

    statement = statement.limit(limit).offset(skip)
    with _session_scope() as session:
        rows = session.execute(statement).scalars()
        return [item for row in rows if (item := _row_to_property(row)) is not None]
