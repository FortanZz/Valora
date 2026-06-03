import pytest


async def _register_and_login(async_client, email: str) -> dict:
    password = "FavoritePass123"
    register_response = await async_client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Favorite",
            "last_name": "User",
        },
    )
    assert register_response.status_code == 201

    login_response = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    auth = login_response.json()
    auth["headers"] = {"Authorization": f"Bearer {auth['access_token']}"}
    return auth


async def _create_property(async_client, headers: dict) -> dict:
    response = await async_client.post(
        "/api/properties/",
        json={
            "title": "Favorite API Apartment",
            "description": "Created for favorite API tests.",
            "location": "Skopje",
            "price": 150000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "favorite-owner@example.com",
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "area_sqm": 78,
            "image_urls": ["https://example.com/favorite-api.jpg"],
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_favorite_add_list_delete_and_duplicate_behavior(async_client):
    owner = await _register_and_login(async_client, "favorite-owner@example.com")
    user = await _register_and_login(async_client, "favorite-user@example.com")
    prop = await _create_property(async_client, owner["headers"])

    first = await async_client.post(
        f"/api/favorites/{prop['id']}",
        headers=user["headers"],
    )
    duplicate = await async_client.post(
        f"/api/favorites/{prop['id']}",
        headers=user["headers"],
    )
    listed = await async_client.get("/api/favorites/", headers=user["headers"])
    deleted = await async_client.delete(
        f"/api/favorites/{prop['id']}",
        headers=user["headers"],
    )
    listed_after_delete = await async_client.get("/api/favorites/", headers=user["headers"])

    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == prop["id"]
    assert listed.json()[0]["image_url"] == "https://example.com/favorite-api.jpg"
    assert deleted.status_code == 204
    assert listed_after_delete.status_code == 200
    assert listed_after_delete.json() == []


@pytest.mark.asyncio
async def test_favorite_missing_property_returns_404(async_client):
    user = await _register_and_login(async_client, "favorite-missing@example.com")

    response = await async_client.post("/api/favorites/999999", headers=user["headers"])

    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


@pytest.mark.asyncio
async def test_favorites_require_authentication(async_client):
    response = await async_client.get("/api/favorites/")

    assert response.status_code == 401
