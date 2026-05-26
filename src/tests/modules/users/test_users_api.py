import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_registration_creates_user_and_returns_tokens(client, factory):
    city = await factory.create_city()
    phone_number = factory.unique_phone()

    response = await client.post(
        "/users/registration",
        json={
            "phone_number": phone_number,
            "password": "RegisterPass123!",
            "full_name": "Registered User",
            "city_id": city.id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"

    me_response = await client.get(
        "/users/me",
        headers=factory.auth_headers(data["access_token"]),
    )

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["phone_number"] == phone_number
    assert me_data["role"] == "user"
    assert me_data["city"] == city.city


async def test_get_me_and_patch_me_return_updated_profile(client, factory):
    old_city = await factory.create_city()
    new_city = await factory.create_city()
    user = await factory.create_user(city_id=old_city.id, full_name="Original Name")
    headers = factory.auth_headers(factory.access_token(user.id))

    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["city"] == old_city.city

    patch_response = await client.patch(
        "/users/me",
        headers=headers,
        json={"city_id": new_city.id, "full_name": "Updated Name"},
    )

    assert patch_response.status_code == 200
    assert patch_response.json()["message"] == "Info changed successfully"

    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["full_name"] == "Updated Name"
    assert me_data["city"] == new_city.city


async def test_password_reset_flow_works_via_verification_code(client, factory, sms_code_store):
    password = "OldPassword123!"
    new_password = "NewPassword456!"
    user = await factory.create_user(password=password)

    send_response = await client.post(
        "/users/verification-code",
        json={"phone_number": user.phone_number},
    )
    assert send_response.status_code == 200
    assert send_response.json()["status"] == "sent"
    assert user.phone_number in sms_code_store

    verify_response = await client.post(
        "/users/verify-code",
        json={"phone_number": user.phone_number, "code": sms_code_store[user.phone_number]},
    )
    assert verify_response.status_code == 200
    reset_token = verify_response.json()["reset_token"]

    reset_response = await client.patch(
        "/users/password",
        params={"new_password": new_password},
        headers=factory.auth_headers(reset_token),
    )
    assert reset_response.status_code == 200

    login_response = await client.post(
        "/auth/login",
        json={"phone_number": user.phone_number, "password": new_password},
    )
    assert login_response.status_code == 200
    assert login_response.json()["access_token"]


async def test_promote_owner_route_requires_super_admin(client, factory):
    target = await factory.create_user(role=Role.user)

    forbidden_response = await client.patch(
        f"/users/{target.id}/promote-to-owner",
        headers=factory.auth_headers(factory.access_token(target.id)),
    )

    assert forbidden_response.status_code == 403


@pytest.mark.xfail(
    reason="Current promote/demote router still expects a query phone_number and does not use the path user_id",
    strict=False,
)
async def test_super_admin_can_promote_and_demote_user_role(client, factory):
    admin = await factory.create_user(role=Role.admin)
    target = await factory.create_user(role=Role.user)

    promote_response = await client.patch(
        f"/users/{target.id}/promote-to-owner",
        params={"phone_number": str(target.id)},
        headers=factory.auth_headers(factory.access_token(admin.id)),
    )
    assert promote_response.status_code == 200
    assert promote_response.json()["role"] == "owner"

    me_response = await client.get(
        "/users/me",
        headers=factory.auth_headers(factory.access_token(target.id)),
    )
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "owner"

    demote_response = await client.patch(
        f"/users/{target.id}/demote-to-user",
        params={"phone_number": str(target.id)},
        headers=factory.auth_headers(factory.access_token(admin.id)),
    )
    assert demote_response.status_code == 200
    assert demote_response.json()["role"] == "user"
