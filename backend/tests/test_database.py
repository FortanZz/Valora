import sqlite3
from datetime import datetime, timedelta

import pytest

from app.database import (
    close_db,
    create_property,
    create_user,
    get_property_by_id,
    get_user_by_email,
    init_db,
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
