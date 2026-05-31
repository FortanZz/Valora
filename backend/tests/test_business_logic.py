def register_user(
    client,
    email: str,
    password: str = "OwnerPass123",
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


def login_user(client, email: str, password: str = "OwnerPass123"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def create_property(client, token: str, **overrides):
    payload = {
        "title": "Test Apartment",
        "description": "A modern city apartment.",
        "location": "Skopje City Center",
        "price": 120000,
        "property_type": "apartment",
        "category": "sale",
        "contact_phone": "+389701234567",
        "contact_email": "owner@example.com",
        "num_bedrooms": 2,
        "num_bathrooms": 1,
        "area_sqm": 75,
    }
    payload.update(overrides)

    response = client.post(
        "/api/properties/",
        json=payload,
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def test_create_property_with_authenticated_user(client):
    register_user(client, "owner1@example.com")
    auth = login_user(client, "owner1@example.com")

    created = create_property(
        client,
        auth["access_token"],
        contact_email="owner1@example.com",
    )

    assert created["title"] == "Test Apartment"
    assert created["owner_id"] == auth["user"]["id"]
    assert created["price"] == 120000


def test_update_property_by_owner(client):
    register_user(client, "owner2@example.com")
    auth = login_user(client, "owner2@example.com")
    created = create_property(
        client,
        auth["access_token"],
        title="Test House",
        description="Spacious family home.",
        location="Suburbia",
        price=180000,
        property_type="house",
        contact_email="owner2@example.com",
        num_bedrooms=3,
        num_bathrooms=2,
        area_sqm=120,
    )

    update_response = client.put(
        f"/api/properties/{created['id']}",
        json={"price": 175000, "description": "Updated price for quick sale."},
        headers=auth_headers(auth["access_token"]),
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["price"] == 175000
    assert updated["description"] == "Updated price for quick sale."


def test_delete_property_denied_for_non_owner(client):
    register_user(client, "owner3@example.com")
    owner_auth = login_user(client, "owner3@example.com")
    created = create_property(
        client,
        owner_auth["access_token"],
        title="Owner3 Property",
        description="Owned by owner3.",
        location="City Outskirts",
        price=95000,
        property_type="house",
        contact_email="owner3@example.com",
    )

    register_user(client, "other@example.com", password="OtherPass123")
    other_auth = login_user(client, "other@example.com", password="OtherPass123")

    delete_response = client.delete(
        f"/api/properties/{created['id']}",
        headers=auth_headers(other_auth["access_token"]),
    )

    assert delete_response.status_code == 403
    assert "permission" in delete_response.json()["detail"].lower()


def test_property_owner_can_delete_and_deleted_property_404s(client):
    register_user(client, "owner4@example.com")
    auth = login_user(client, "owner4@example.com")
    created = create_property(client, auth["access_token"])

    delete_response = client.delete(
        f"/api/properties/{created['id']}",
        headers=auth_headers(auth["access_token"]),
    )
    missing_response = client.get(f"/api/properties/{created['id']}")

    assert delete_response.status_code == 204
    assert missing_response.status_code == 404


def test_property_mutations_require_authentication(client):
    create_response = client.post(
        "/api/properties/",
        json={
            "title": "Unauthorized Apartment",
            "location": "Skopje",
            "price": 100000,
            "property_type": "apartment",
            "category": "sale",
            "contact_phone": "+389701234567",
            "contact_email": "owner@example.com",
        },
    )
    update_response = client.put("/api/properties/1", json={"price": 110000})
    delete_response = client.delete("/api/properties/1")

    assert create_response.status_code == 401
    assert update_response.status_code == 401
    assert delete_response.status_code == 401


def test_search_filters_and_sorting_can_be_combined(client):
    register_user(client, "search-owner@example.com")
    auth = login_user(client, "search-owner@example.com")
    token = auth["access_token"]

    create_property(
        client,
        token,
        title="Downtown Apartment",
        description="Near the main square.",
        location="Skopje Center",
        price=120000,
        property_type="apartment",
        category="sale",
    )
    create_property(
        client,
        token,
        title="Lake View House",
        description="Family house near the lake.",
        location="Ohrid",
        price=250000,
        property_type="house",
        category="sale",
    )
    create_property(
        client,
        token,
        title="Central Office",
        description="Office space for rent.",
        location="Skopje Center",
        price=900,
        property_type="office",
        category="rent",
        num_bedrooms=None,
        num_bathrooms=None,
    )

    filtered = client.get(
        "/api/properties/search",
        params={
            "query": "downtown",
            "min_price": 100000,
            "max_price": 200000,
            "property_type": "apartment",
            "category": "sale",
            "location": "skopje",
        },
    )
    sorted_sale = client.get(
        "/api/properties/search",
        params={"category": "sale", "sort_by": "price-desc"},
    )

    assert filtered.status_code == 200
    assert [item["title"] for item in filtered.json()] == ["Downtown Apartment"]
    assert sorted_sale.status_code == 200
    assert [item["price"] for item in sorted_sale.json()] == [250000, 120000]


def test_land_rules_are_enforced_on_create_and_update(client):
    register_user(client, "land-owner@example.com")
    auth = login_user(client, "land-owner@example.com")

    rent_land_response = client.post(
        "/api/properties/",
        json={
            "title": "Land Plot",
            "location": "Tetovo",
            "price": 50000,
            "property_type": "land",
            "category": "rent",
            "contact_phone": "+389701234567",
            "contact_email": "land@example.com",
        },
        headers=auth_headers(auth["access_token"]),
    )
    sale_land = create_property(
        client,
        auth["access_token"],
        title="Land Plot",
        location="Tetovo",
        price=50000,
        property_type="land",
        category="sale",
        num_bedrooms=None,
        num_bathrooms=None,
        area_sqm=700,
    )
    invalid_update = client.put(
        f"/api/properties/{sale_land['id']}",
        json={"num_bedrooms": 1},
        headers=auth_headers(auth["access_token"]),
    )

    assert rent_land_response.status_code == 422
    assert invalid_update.status_code == 400
