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
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    func,
    or_,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError as SQLAlchemyIntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, joinedload, mapped_column, relationship, sessionmaker
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
    favorites: Mapped[list["FavoriteRecord"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sent_messages: Mapped[list["MessageRecord"]] = relationship(
        back_populates="sender",
        cascade="all, delete-orphan",
        foreign_keys="MessageRecord.sender_id",
    )
    received_messages: Mapped[list["MessageRecord"]] = relationship(
        back_populates="recipient",
        cascade="all, delete-orphan",
        foreign_keys="MessageRecord.recipient_id",
    )


class PropertyRecord(Base):
    __tablename__ = "properties"
    __table_args__ = (
        Index("ix_properties_category_type_price", "category", "property_type", "price"),
        Index("ix_properties_owner_created", "owner_id", "created_at"),
    )

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
    images: Mapped[list["PropertyImageRecord"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
        order_by="PropertyImageRecord.sort_order",
    )
    favorites: Mapped[list["FavoriteRecord"]] = relationship(
        back_populates="property",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["MessageRecord"]] = relationship(back_populates="property")


class PropertyImageRecord(Base):
    __tablename__ = "property_images"
    __table_args__ = (
        Index("ix_property_images_property_order", "property_id", "sort_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    property: Mapped[PropertyRecord] = relationship(back_populates="images")


class FavoriteRecord(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "property_id", name="uq_favorites_user_property"),
        Index("ix_favorites_user_created", "user_id", "created_at"),
        Index("ix_favorites_property_created", "property_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped[UserRecord] = relationship(back_populates="favorites")
    property: Mapped[PropertyRecord] = relationship(back_populates="favorites")


class MessageRecord(Base):
    __tablename__ = "messages"
    __table_args__ = (
        Index("ix_messages_recipient_created", "recipient_id", "created_at"),
        Index("ix_messages_sender_created", "sender_id", "created_at"),
        Index("ix_messages_property_created", "property_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    property_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("properties.id", ondelete="SET NULL"),
        index=True,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    sender: Mapped[UserRecord] = relationship(
        back_populates="sent_messages",
        foreign_keys=[sender_id],
    )
    recipient: Mapped[UserRecord] = relationship(
        back_populates="received_messages",
        foreign_keys=[recipient_id],
    )
    property: Mapped[Optional[PropertyRecord]] = relationship(back_populates="messages")


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
        _ensure_sqlite_indexes(ENGINE)
    return ENGINE


def _ensure_sqlite_indexes(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_properties_category_type_price
                ON properties(category, property_type, price)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_properties_owner_created
                ON properties(owner_id, created_at)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_property_images_property_order
                ON property_images(property_id, sort_order)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_favorites_user_created
                ON favorites(user_id, created_at)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_favorites_property_created
                ON favorites(property_id, created_at)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_messages_recipient_created
                ON messages(recipient_id, created_at)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_messages_sender_created
                ON messages(sender_id, created_at)
                """
            )
        )
        connection.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_messages_property_created
                ON messages(property_id, created_at)
                """
            )
        )


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
    image_urls = [image.url for image in row.images]
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
        "image_url": image_urls[0] if image_urls else None,
        "image_urls": image_urls,
    }


def _row_to_favorite(row: Optional[FavoriteRecord]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row.id,
        "user_id": row.user_id,
        "property_id": row.property_id,
        "created_at": row.created_at,
    }


def _row_to_message(row: Optional[MessageRecord]) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    return {
        "id": row.id,
        "sender_id": row.sender_id,
        "recipient_id": row.recipient_id,
        "property_id": row.property_id,
        "body": row.body,
        "created_at": row.created_at,
        "read_at": row.read_at,
    }


def _property_select_with_images():
    return select(PropertyRecord).options(joinedload(PropertyRecord.images))


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
    image_urls: Optional[List[str]] = None,
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
        for index, url in enumerate(image_urls or []):
            cleaned_url = url.strip()
            if cleaned_url:
                property_item.images.append(
                    PropertyImageRecord(
                        url=cleaned_url,
                        alt_text=title,
                        sort_order=index,
                        created_at=created_at,
                    )
                )
        session.add(property_item)
        session.flush()
        return _row_to_property(property_item) or {}


def get_property_by_id(property_id: int) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        row = session.execute(
            _property_select_with_images().where(PropertyRecord.id == property_id)
        ).unique().scalar_one_or_none()
        return _row_to_property(row)


def get_properties_by_owner(owner_id: int) -> List[Dict[str, Any]]:
    with _session_scope() as session:
        rows = session.execute(
            _property_select_with_images()
            .where(PropertyRecord.owner_id == owner_id)
            .order_by(PropertyRecord.created_at.desc(), PropertyRecord.id.desc())
        ).unique().scalars()
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


def favorite_property(
    user_id: int,
    property_id: int,
    created_at: datetime,
) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        if session.get(PropertyRecord, property_id) is None:
            return None

        existing = session.execute(
            select(FavoriteRecord).where(
                FavoriteRecord.user_id == user_id,
                FavoriteRecord.property_id == property_id,
            )
        ).scalar_one_or_none()
        if existing is not None:
            return _row_to_favorite(existing)

        favorite = FavoriteRecord(
            user_id=user_id,
            property_id=property_id,
            created_at=created_at,
        )
        session.add(favorite)
        session.flush()
        return _row_to_favorite(favorite)


def remove_favorite(user_id: int, property_id: int) -> bool:
    with _session_scope() as session:
        favorite = session.execute(
            select(FavoriteRecord).where(
                FavoriteRecord.user_id == user_id,
                FavoriteRecord.property_id == property_id,
            )
        ).scalar_one_or_none()
        if favorite is None:
            return False
        session.delete(favorite)
        return True


def is_property_favorited(user_id: int, property_id: int) -> bool:
    with _session_scope() as session:
        row = session.execute(
            select(func.count())
            .select_from(FavoriteRecord)
            .where(
                FavoriteRecord.user_id == user_id,
                FavoriteRecord.property_id == property_id,
            )
        ).scalar_one()
        return int(row) > 0


def get_favorite_properties(user_id: int) -> List[Dict[str, Any]]:
    with _session_scope() as session:
        rows = session.execute(
            select(FavoriteRecord)
            .options(
                joinedload(FavoriteRecord.property).joinedload(PropertyRecord.images)
            )
            .where(FavoriteRecord.user_id == user_id)
            .order_by(FavoriteRecord.created_at.desc(), FavoriteRecord.id.desc())
        ).unique().scalars()
        return [
            property_item
            for favorite in rows
            if (property_item := _row_to_property(favorite.property)) is not None
        ]


def create_property_message(
    sender_id: int,
    property_id: int,
    body: str,
    created_at: datetime,
) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        property_item = session.get(PropertyRecord, property_id)
        if property_item is None:
            return None

        message = MessageRecord(
            sender_id=sender_id,
            recipient_id=property_item.owner_id,
            property_id=property_id,
            body=body,
            created_at=created_at,
        )
        session.add(message)
        session.flush()
        return _row_to_message(message)


def get_message_by_id(message_id: int) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        return _row_to_message(session.get(MessageRecord, message_id))


def get_received_messages(user_id: int) -> List[Dict[str, Any]]:
    with _session_scope() as session:
        rows = session.execute(
            select(MessageRecord)
            .where(MessageRecord.recipient_id == user_id)
            .order_by(MessageRecord.created_at.desc(), MessageRecord.id.desc())
        ).scalars()
        return [item for row in rows if (item := _row_to_message(row)) is not None]


def get_sent_messages(user_id: int) -> List[Dict[str, Any]]:
    with _session_scope() as session:
        rows = session.execute(
            select(MessageRecord)
            .where(MessageRecord.sender_id == user_id)
            .order_by(MessageRecord.created_at.desc(), MessageRecord.id.desc())
        ).scalars()
        return [item for row in rows if (item := _row_to_message(row)) is not None]


def mark_message_read(message_id: int, read_at: datetime) -> Optional[Dict[str, Any]]:
    with _session_scope() as session:
        message = session.get(MessageRecord, message_id)
        if message is None:
            return None
        message.read_at = read_at
        session.flush()
        return _row_to_message(message)


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
    statement = _property_select_with_images()
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
        rows = session.execute(statement).unique().scalars()
        return [item for row in rows if (item := _row_to_property(row)) is not None]
