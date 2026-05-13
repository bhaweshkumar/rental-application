"""Phase 2 — authentication tests for FastAPI auth endpoints."""
from fastapi.testclient import TestClient


def test_auth_register_login_and_me_cycle(client: TestClient):
    register_payload = {
        "email": "test_auth@example.com",
        "display_name": "Auth Tester",
        "password": "securepassword",
    }
    register_response = client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["success"] is True
    assert "access_token" in register_data["data"]
    assert "refresh_token" in register_data["data"]

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_auth@example.com", "password": "securepassword"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["success"] is True
    token = login_data["data"]["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["success"] is True
    assert me_data["data"]["email"] == "test_auth@example.com"

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["data"]["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert refresh_data["success"] is True
    assert refresh_data["data"]["access_token"] != token

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": login_data["data"]["refresh_token"]},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["success"] is True

    refresh_again = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": login_data["data"]["refresh_token"]},
    )
    assert refresh_again.status_code == 401


def test_login_with_wrong_password_returns_401(client: TestClient):
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_wrong_password@example.com",
            "display_name": "Auth Tester",
            "password": "correctpassword",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test_wrong_password@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_register_duplicate_email_returns_409(client: TestClient):
    payload = {
        "email": "duplicate@example.com",
        "display_name": "Dupe User",
        "password": "securepassword",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 200

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
