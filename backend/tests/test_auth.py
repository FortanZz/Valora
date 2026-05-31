def register_payload(email="user@example.com", password="SecurePass123"):
    return {
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "User",
    }


def test_register_login_me_and_refresh_flow(client):
    register_response = client.post(
        "/api/auth/register",
        json=register_payload(email="flow@example.com"),
    )

    assert register_response.status_code == 201
    registered = register_response.json()
    assert registered["token_type"] == "bearer"
    assert registered["access_token"]
    assert registered["refresh_token"]
    assert registered["user"]["email"] == "flow@example.com"
    assert "hashed_password" not in registered["user"]

    login_response = client.post(
        "/api/auth/login",
        json={"email": "flow@example.com", "password": "SecurePass123"},
    )
    assert login_response.status_code == 200
    login = login_response.json()

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "flow@example.com"

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": login["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    assert refresh_response.json()["access_token"]


def test_duplicate_registration_is_rejected(client):
    first_response = client.post(
        "/api/auth/register",
        json=register_payload(email="duplicate@example.com"),
    )
    duplicate_response = client.post(
        "/api/auth/register",
        json=register_payload(email="duplicate@example.com"),
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/auth/register",
        json=register_payload(email="wrong-password@example.com"),
    )

    response = client.post(
        "/api/auth/login",
        json={"email": "wrong-password@example.com", "password": "BadPass123"},
    )

    assert response.status_code == 401


def test_me_requires_valid_access_token(client):
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_refresh_rejects_access_token(client):
    register_response = client.post(
        "/api/auth/register",
        json=register_payload(email="token-type@example.com"),
    )
    access_token = register_response.json()["access_token"]

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401
