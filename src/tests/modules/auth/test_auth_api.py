import pytest


pytestmark = pytest.mark.asyncio


async def test_login_returns_tokens_for_valid_credentials(client, factory):
    password = "LoginPass123!"
    user = await factory.create_user(password=password)

    response = await client.post(
        "/auth/login",
        json={"phone_number": user.phone_number, "password": password},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


async def test_login_rejects_invalid_password(client, factory):
    user = await factory.create_user(password="CorrectPass123!")

    response = await client.post(
        "/auth/login",
        json={"phone_number": user.phone_number, "password": "WrongPass123!"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong login or password"


async def test_refresh_returns_new_tokens_for_valid_refresh_token(client, factory):
    user = await factory.create_user()

    response = await client.post(
        "/auth/refresh",
        headers=factory.auth_headers(factory.refresh_token(user.id)),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]
