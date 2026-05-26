import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_owner_can_create_computers_and_staff_admin_can_toggle_power(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    staff_admin = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    await factory.create_staff_member(club_id=club.id, user_id=staff_admin.id, staff_role="admin")

    create_response = await client.post(
        "/computers/",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(owner.id)),
        json=[{"number": 1, "specification": "RTX 4060", "zone_id": zone.id, "x": 1.0, "y": 2.0}],
    )
    assert create_response.status_code == 200

    list_response = await client.get("/computers/", params={"zone_id": zone.id})
    assert list_response.status_code == 200
    computers = list_response.json()
    assert len(computers) == 1
    computer_id = computers[0]["id"]
    assert computers[0]["is_active"] is True

    power_off_response = await client.post(
        f"/computers/{computer_id}/turn-off",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(staff_admin.id)),
    )
    assert power_off_response.status_code == 200
    assert power_off_response.json() is True

    list_response = await client.get("/computers/", params={"zone_id": zone.id})
    assert list_response.json()[0]["is_active"] is False

    power_on_response = await client.post(
        f"/computers/{computer_id}/turn-on",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(staff_admin.id)),
    )
    assert power_on_response.status_code == 200
    assert power_on_response.json() is True
