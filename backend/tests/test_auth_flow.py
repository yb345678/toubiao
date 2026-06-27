from fastapi.testclient import TestClient

from app.main import app


def test_register_login_and_me():
    client = TestClient(app)
    email = "demo@example.com"
    password = "Passw0rd!"

    register = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": "demo", "password": password},
    )
    assert register.status_code in (200, 400)

    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token.count(".") == 2

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == email
