import pytest


async def _register_and_login(async_client, email: str) -> dict:
    password = "MessagePass123"
    register_response = await async_client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Message",
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


async def _create_property(async_client, owner: dict) -> dict:
    response = await async_client.post(
        "/api/properties/",
        json={
            "title": "Message API Apartment",
            "description": "Created for message API tests.",
            "location": "Skopje",
            "price": 150000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": owner["user"]["email"],
            "num_bedrooms": 2,
            "num_bathrooms": 1,
            "area_sqm": 78,
        },
        headers=owner["headers"],
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_property_message_send_inbox_sent_and_mark_read(async_client):
    owner = await _register_and_login(async_client, "message-owner@example.com")
    sender = await _register_and_login(async_client, "message-sender@example.com")
    prop = await _create_property(async_client, owner)

    created = await async_client.post(
        "/api/messages/",
        json={
            "property_id": prop["id"],
            "body": "Is this property still available?",
        },
        headers=sender["headers"],
    )
    inbox = await async_client.get("/api/messages/inbox", headers=owner["headers"])
    sent = await async_client.get("/api/messages/sent", headers=sender["headers"])
    forbidden_read = await async_client.put(
        f"/api/messages/{created.json()['id']}/read",
        headers=sender["headers"],
    )
    marked_read = await async_client.put(
        f"/api/messages/{created.json()['id']}/read",
        headers=owner["headers"],
    )

    assert created.status_code == 201
    data = created.json()
    assert data["sender_id"] == sender["user"]["id"]
    assert data["recipient_id"] == owner["user"]["id"]
    assert data["property_id"] == prop["id"]
    assert data["read_at"] is None
    assert inbox.status_code == 200
    assert inbox.json()[0]["id"] == data["id"]
    assert sent.status_code == 200
    assert sent.json()[0]["id"] == data["id"]
    assert forbidden_read.status_code == 403
    assert marked_read.status_code == 200
    assert marked_read.json()["read_at"] is not None


@pytest.mark.asyncio
async def test_message_missing_property_returns_404(async_client):
    sender = await _register_and_login(async_client, "message-missing@example.com")

    response = await async_client.post(
        "/api/messages/",
        json={"property_id": 999999, "body": "Is this available?"},
        headers=sender["headers"],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Property not found"


@pytest.mark.asyncio
async def test_message_to_own_property_is_rejected(async_client):
    owner = await _register_and_login(async_client, "message-self@example.com")
    prop = await _create_property(async_client, owner)

    response = await async_client.post(
        "/api/messages/",
        json={"property_id": prop["id"], "body": "Is this available?"},
        headers=owner["headers"],
    )

    assert response.status_code == 400
    assert "yourself" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_messages_require_authentication(async_client):
    response = await async_client.get("/api/messages/inbox")

    assert response.status_code == 401
