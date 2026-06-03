import sqlite3
from datetime import datetime, timedelta

import pytest
from sqlalchemy import inspect

from app import database as database_module
from app.database import (
    close_db,
    create_property,
    create_property_message,
    create_user,
    delete_property,
    favorite_property,
    get_favorite_properties,
    get_message_by_id,
    get_property_by_id,
    get_received_messages,
    get_sent_messages,
    get_user_by_email,
    init_db,
    is_property_favorited,
    mark_message_read,
    remove_favorite,
    search_properties,
    update_property,
)


def create_test_user(email="db-owner@example.com"):
    return create_user(
        email=email,
        first_name="Database",
        last_name="Owner",
        hashed_password="hashed-password",
        created_at=datetime(2026, 5, 31, 10, 0, 0),
    )


def create_test_property(owner_id, **overrides):
    created_at = overrides.pop("created_at", datetime(2026, 5, 31, 12, 0, 0))
    payload = {
        "owner_id": owner_id,
        "title": "Database Apartment",
        "description": "Stored in SQLite.",
        "location": "Skopje",
        "price": 150000,
        "property_type": "apartment",
        "category": "sale",
        "contact_phone": "+389701234567",
        "contact_email": "db-owner@example.com",
        "num_bedrooms": 2,
        "num_bathrooms": 1,
        "area_sqm": 80,
        "created_at": created_at,
        "updated_at": created_at,
    }
    payload.update(overrides)
    return create_property(**payload)


def test_sqlite_records_survive_connection_reinitialization(tmp_path):
    db_path = tmp_path / "persistent.db"
    init_db(str(db_path))
    user = create_test_user()
    prop = create_test_property(user["id"])

    close_db()
    init_db(str(db_path))

    stored_user = get_user_by_email("db-owner@example.com")
    stored_property = get_property_by_id(prop["id"])

    assert stored_user["id"] == user["id"]
    assert stored_user["created_at"] == datetime(2026, 5, 31, 10, 0, 0)
    assert stored_property["title"] == "Database Apartment"
    assert stored_property["created_at"] == datetime(2026, 5, 31, 12, 0, 0)


def test_property_update_allows_only_known_mutable_fields():
    user = create_test_user()
    prop = create_test_property(user["id"])

    updated = update_property(
        prop["id"],
        updates={
            "price": 145000,
            "description": "Updated description.",
            "owner_id": 999,
            "property_type": "land",
        },
        updated_at=datetime(2026, 5, 31, 13, 0, 0),
    )

    assert updated["price"] == 145000
    assert updated["description"] == "Updated description."
    assert updated["owner_id"] == user["id"]
    assert updated["property_type"] == "apartment"
    assert updated["updated_at"] == datetime(2026, 5, 31, 13, 0, 0)


def test_search_properties_combines_filters_and_pagination():
    user = create_test_user()
    create_test_property(
        user["id"],
        title="Affordable Apartment",
        location="Skopje Center",
        price=110000,
        created_at=datetime(2026, 5, 31, 12, 0, 0),
    )
    create_test_property(
        user["id"],
        title="Premium Apartment",
        location="Skopje Center",
        price=250000,
        created_at=datetime(2026, 5, 31, 12, 1, 0),
    )
    create_test_property(
        user["id"],
        title="Ohrid House",
        location="Ohrid",
        price=180000,
        property_type="house",
        created_at=datetime(2026, 5, 31, 12, 2, 0),
    )

    results = search_properties(
        query="apartment",
        min_price=100000,
        max_price=300000,
        property_type="apartment",
        category="sale",
        location="skopje",
        sort_by="price-asc",
        skip=1,
        limit=1,
    )

    assert len(results) == 1
    assert results[0]["title"] == "Premium Apartment"


def test_property_images_are_persisted_in_order():
    user = create_test_user()
    prop = create_test_property(
        user["id"],
        image_urls=[
            "https://example.com/front.jpg",
            "https://example.com/kitchen.jpg",
        ],
    )

    stored = get_property_by_id(prop["id"])
    search_result = search_properties(query="database", limit=1)[0]

    assert stored["image_url"] == "https://example.com/front.jpg"
    assert stored["image_urls"] == [
        "https://example.com/front.jpg",
        "https://example.com/kitchen.jpg",
    ]
    assert search_result["image_urls"] == stored["image_urls"]


def test_property_image_table_and_query_indexes_exist():
    engine = database_module.ENGINE
    assert engine is not None

    inspector = inspect(engine)
    property_indexes = {index["name"] for index in inspector.get_indexes("properties")}
    image_indexes = {index["name"] for index in inspector.get_indexes("property_images")}
    favorite_indexes = {index["name"] for index in inspector.get_indexes("favorites")}
    message_indexes = {index["name"] for index in inspector.get_indexes("messages")}
    favorite_uniques = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("favorites")
    }

    assert "property_images" in inspector.get_table_names()
    assert "favorites" in inspector.get_table_names()
    assert "messages" in inspector.get_table_names()
    assert "ix_properties_category_type_price" in property_indexes
    assert "ix_properties_owner_created" in property_indexes
    assert "ix_property_images_property_order" in image_indexes
    assert "ix_favorites_user_created" in favorite_indexes
    assert "ix_favorites_property_created" in favorite_indexes
    assert "uq_favorites_user_property" in favorite_uniques
    assert "ix_messages_recipient_created" in message_indexes
    assert "ix_messages_sender_created" in message_indexes
    assert "ix_messages_property_created" in message_indexes


def test_favorites_are_unique_and_list_favorited_properties():
    user = create_test_user("favorite-user@example.com")
    prop = create_test_property(
        user["id"],
        title="Favorite Apartment",
        image_urls=["https://example.com/favorite.jpg"],
    )

    first = favorite_property(
        user_id=user["id"],
        property_id=prop["id"],
        created_at=datetime(2026, 5, 31, 13, 0, 0),
    )
    duplicate = favorite_property(
        user_id=user["id"],
        property_id=prop["id"],
        created_at=datetime(2026, 5, 31, 14, 0, 0),
    )
    favorites = get_favorite_properties(user["id"])

    assert first["id"] == duplicate["id"]
    assert is_property_favorited(user["id"], prop["id"]) is True
    assert len(favorites) == 1
    assert favorites[0]["id"] == prop["id"]
    assert favorites[0]["image_url"] == "https://example.com/favorite.jpg"

    assert remove_favorite(user["id"], prop["id"]) is True
    assert remove_favorite(user["id"], prop["id"]) is False
    assert is_property_favorited(user["id"], prop["id"]) is False


def test_favorite_relationships_survive_property_delete():
    user = create_test_user("cascade-favorite-user@example.com")
    prop = create_test_property(user["id"], title="Temporary Favorite")
    favorite_property(user["id"], prop["id"], datetime(2026, 5, 31, 13, 0, 0))

    delete_property(prop["id"])

    assert get_favorite_properties(user["id"]) == []


def test_messages_create_list_and_mark_read():
    owner = create_test_user("message-owner@example.com")
    sender = create_test_user("message-sender@example.com")
    prop = create_test_property(
        owner["id"],
        title="Message Apartment",
        contact_email="message-owner@example.com",
    )

    message = create_property_message(
        sender_id=sender["id"],
        property_id=prop["id"],
        body="Is this property available?",
        created_at=datetime(2026, 5, 31, 13, 0, 0),
    )
    read = mark_message_read(
        message["id"],
        read_at=datetime(2026, 5, 31, 14, 0, 0),
    )

    assert message["sender_id"] == sender["id"]
    assert message["recipient_id"] == owner["id"]
    assert get_received_messages(owner["id"])[0]["id"] == message["id"]
    assert get_sent_messages(sender["id"])[0]["id"] == message["id"]
    assert read["read_at"] == datetime(2026, 5, 31, 14, 0, 0)
    assert get_message_by_id(message["id"])["read_at"] == datetime(2026, 5, 31, 14, 0, 0)


def test_message_history_keeps_null_property_after_property_delete():
    owner = create_test_user("message-delete-owner@example.com")
    sender = create_test_user("message-delete-sender@example.com")
    prop = create_test_property(owner["id"], title="Message Delete Apartment")
    message = create_property_message(
        sender_id=sender["id"],
        property_id=prop["id"],
        body="Is this still listed?",
        created_at=datetime(2026, 5, 31, 13, 0, 0),
    )

    delete_property(prop["id"])

    assert get_message_by_id(message["id"])["property_id"] is None


def test_foreign_key_prevents_orphan_properties():
    now = datetime.utcnow()

    with pytest.raises(sqlite3.IntegrityError):
        create_property(
            owner_id=999,
            title="Orphan Property",
            description=None,
            location="Skopje",
            price=100000,
            property_type="apartment",
            category="sale",
            contact_phone="+389701234567",
            contact_email="orphan@example.com",
            num_bedrooms=1,
            num_bathrooms=1,
            area_sqm=50,
            created_at=now,
            updated_at=now + timedelta(seconds=1),
        )
