import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


def build_zone_payload(club_id: int, name: str = "Standard", cost: int = 500) -> dict:
    return {
        "name": name,
        "cost": cost,
        "cpu": "Ryzen 5",
        "gpu": "RTX 4060",
        "ram": "16GB",
        "ssd": "1TB",
        "monitor": "144Hz",
        "x": 10.0,
        "y": 20.0,
        "club_id": club_id,
    }


async def test_owner_can_create_update_and_delete_zones(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    headers = factory.auth_headers(factory.access_token(owner.id))

    create_response = await client.post(
        "/zones/",
        params={"club_id": club.id},
        headers=headers,
        json=[build_zone_payload(club.id)],
    )
    assert create_response.status_code == 200

    list_response = await client.get("/zones/", params={"club_id": club.id})
    assert list_response.status_code == 200
    zones = list_response.json()
    assert len(zones) == 1
    zone_id = zones[0]["id"]
    assert zones[0]["name"] == "Standard"

    update_response = await client.patch(
        f"/zones/{zone_id}",
        params={"club_id": club.id},
        headers=headers,
        json=[{**build_zone_payload(club.id, name="VIP", cost=900), "id": zone_id}],
    )
    assert update_response.status_code == 200

    list_response = await client.get("/zones/", params={"club_id": club.id})
    updated_zone = list_response.json()[0]
    assert updated_zone["name"] == "VIP"
    assert updated_zone["cost"] == 900

    delete_response = await client.delete(
        f"/zones/{zone_id}",
        params={"club_id": club.id},
        headers=headers,
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == 1

    list_response = await client.get("/zones/", params={"club_id": club.id})
    assert list_response.status_code == 200
    assert list_response.json() == []
