import pytest
from fastapi.testclient import TestClient

def test_auth_register(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test_auth@example.com",
            "password": "securepassword",
            "display_name": "Auth Tester"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_auth@example.com"
    assert "id" in data

def test_auth_login(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test_auth@example.com",
            "password": "securepassword"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    
def test_auth_me(client: TestClient):
    login_response = client.post("/api/v1/auth/login", data={"username": "test_auth@example.com", "password": "securepassword"})
    token = login_response.json()["access_token"]
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_auth@example.com"