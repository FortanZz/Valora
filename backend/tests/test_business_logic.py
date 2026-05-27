from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def register_user(
    email: str,
    password: str,
    first_name: str = "Test",
    last_name: str = "User",
):
    response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(email: str, password: str):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def test_create_property_with_authenticated_user():
    register_user("owner1@example.com", "OwnerPass123")
    auth = login_user("owner1@example.com", "OwnerPass123")
    access_token = auth["access_token"]

    property_payload = {
        "title": "Test Apartment",
        "description": "A modern city apartment.",
        "location": "Skopje City Center",
        "price": 120000,
        "property_type": "apartment",
        "category": "sale",
        "contact_phone": "+389701234567",
        "contact_email": "owner1@example.com",
        "num_bedrooms": 2,
        "num_bathrooms": 1,
        "area_sqm": 75,
    }

    response = client.post(
        "/api/properties/",
        json=property_payload,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Apartment"
    assert data["owner_id"] == 1
    assert data["price"] == 120000


def test_update_property_by_owner():
    register_user("owner2@example.com", "OwnerPass123")
    auth = login_user("owner2@example.com", "OwnerPass123")
    access_token = auth["access_token"]

    response = client.post(
        "/api/properties/",
        json={
            "title": "Test House",
            "description": "Spacious family home.",
            "location": "Suburbia",
            "price": 180000,
            "property_type": "house",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "owner2@example.com",
            "num_bedrooms": 3,
            "num_bathrooms": 2,
            "area_sqm": 120,
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    prop_id = response.json()["id"]

    update_response = client.put(
        f"/api/properties/{prop_id}",
        json={"price": 175000, "description": "Updated price for quick sale."},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["price"] == 175000
    assert updated["description"] == "Updated price for quick sale."


def test_delete_property_denied_for_non_owner():
    register_user("owner3@example.com", "OwnerPass123")
    owner_auth = login_user("owner3@example.com", "OwnerPass123")
    owner_token = owner_auth["access_token"]

    response = client.post(
        "/api/properties/",
        json={
            "title": "Owner3 Property",
            "description": "Owned by owner3.",
            "location": "City Outskirts",
            "price": 95000,
            "property_type": "house",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "owner3@example.com",
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "area_sqm": 90,
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code == 201
    prop_id = response.json()["id"]

    register_user("other@example.com", "OtherPass123")
    other_auth = login_user("other@example.com", "OtherPass123")
    other_token = other_auth["access_token"]

    delete_response = client.delete(
        f"/api/properties/{prop_id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert delete_response.status_code == 403
    assert "permission" in delete_response.json()["detail"].lower()
