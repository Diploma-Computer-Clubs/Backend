import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_owner_can_add_list_and_delete_staff_member(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    staff_user = await factory.create_user(city_id=city.id, full_name="Staff User")
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    headers = factory.auth_headers(factory.access_token(owner.id))

    add_response = await client.post(
        f"/clubs/{club.id}/staff",
        headers=headers,
        json={"phone_number": staff_user.phone_number, "staff_role": "admin"},
    )
    assert add_response.status_code == 200

    list_response = await client.get(f"/clubs/{club.id}/staff", headers=headers)
    assert list_response.status_code == 200
    staff_items = list_response.json()
    assert len(staff_items) == 1
    assert staff_items[0]["staff_role"] == "admin"

    delete_response = await client.delete(
        f"/clubs/{club.id}/staff",
        params={"staff_id": staff_user.id},
        headers=headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == 1
