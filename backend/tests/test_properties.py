import pytest


async def _auth_headers(async_client, email: str = "owner@example.com") -> dict[str, str]:
    password = "OwnerPass123"
    register_payload = {
        "email": email,
        "password": password,
        "first_name": "Owner",
        "last_name": "User",
    }
    register_response = await async_client.post("/api/auth/register", json=register_payload)
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _property_payload() -> dict:
    return {
        "title": "Modern Apartment",
        "description": "Close to city center.",
        "location": "Skopje",
        "price": 150000,
        "property_type": "apartment",
        "category": "sale",
        "contact_phone": "+389701234567",
        "contact_email": "owner@example.com",
        "num_bedrooms": 2,
        "num_bathrooms": 1,
        "area_sqm": 78,
    }


@pytest.mark.asyncio
async def test_create_property(async_client):
    headers = await _auth_headers(async_client)
    response = await async_client.post("/api/properties/", json=_property_payload(), headers=headers)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] > 0
    assert data["title"] == "Modern Apartment"


@pytest.mark.asyncio
async def test_get_property(async_client):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/api/properties/",
        json=_property_payload(),
        headers=headers,
    )
    property_id = create_response.json()["id"]

    response = await async_client.get(f"/api/properties/{property_id}")

    assert response.status_code == 200
    assert response.json()["id"] == property_id


@pytest.mark.asyncio
async def test_list_properties(async_client):
    headers = await _auth_headers(async_client)
    await async_client.post("/api/properties/", json=_property_payload(), headers=headers)

    response = await async_client.get("/api/properties/?skip=0&limit=10")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_property(async_client):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/api/properties/",
        json=_property_payload(),
        headers=headers,
    )
    property_id = create_response.json()["id"]

    response = await async_client.put(
        f"/api/properties/{property_id}",
        json={"title": "Updated Apartment"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Apartment"


@pytest.mark.asyncio
async def test_delete_property(async_client):
    headers = await _auth_headers(async_client)
    create_response = await async_client.post(
        "/api/properties/",
        json=_property_payload(),
        headers=headers,
    )
    property_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/properties/{property_id}", headers=headers)
    get_response = await async_client.get(f"/api/properties/{property_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_get_missing_property_returns_404(async_client):
    response = await async_client.get("/api/properties/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"
