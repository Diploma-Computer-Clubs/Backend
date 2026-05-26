from datetime import timedelta

import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


def build_club_payload(city_id: int, city_name: str, address: str) -> dict:
    return {
        "name": "Cyber Arena",
        "address": address,
        "image_url": "https://example.com/club.png",
        "description": "Best gaming club",
        "city_id": city_id,
        "city_name": city_name,
        "promos": [],
    }


async def test_owner_can_create_club_and_fetch_it_in_search_map_and_count(client, factory):
    city = await factory.create_city(city_name="Astana")
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    payload = build_club_payload(city.id, city.city, factory.unique_text("Address"))
    headers = factory.auth_headers(factory.access_token(owner.id))

    create_response = await client.post("/clubs", json=payload, headers=headers)
    assert create_response.status_code == 200
    assert create_response.json()["message"] == "Club successfully added"

    search_response = await client.get("/clubs/search", params={"city_id": city.id})
    assert search_response.status_code == 200
    assert len(search_response.json()) == 1
    assert search_response.json()[0]["name"] == payload["name"]

    count_response = await client.get("/clubs/count", params={"city_id": city.id})
    assert count_response.status_code == 200
    assert count_response.json()["total_clubs"] == 1

    map_response = await client.get("/clubs/map", params={"city_id": city.id})
    assert map_response.status_code == 200
    assert len(map_response.json()) == 1
    assert map_response.json()[0]["latitude"] is not None
    assert map_response.json()[0]["longitude"] is not None


async def test_non_owner_cannot_create_club(client, factory):
    city = await factory.create_city(city_name="Astana")
    regular_user = await factory.create_user(role=Role.user, city_id=city.id)
    payload = build_club_payload(city.id, city.city, factory.unique_text("Address"))

    response = await client.post(
        "/clubs",
        json=payload,
        headers=factory.auth_headers(factory.access_token(regular_user.id)),
    )

    assert response.status_code == 403


async def test_club_availability_returns_zone_map_with_existing_bookings(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    booker = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    start_time, end_time = factory.booking_window()
    await factory.create_booking(
        user_id=booker.id,
        club_id=club.id,
        zone_id=zone.id,
        computer_id=computer.id,
        start_time=start_time,
        end_time=end_time,
        total_price=1500,
    )

    response = await client.get(
        f"/clubs/{club.id}/availability",
        params={
            "start_time": (start_time - timedelta(minutes=15)).isoformat(),
            "end_time": (end_time + timedelta(minutes=15)).isoformat(),
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == zone.id
    assert len(data[0]["computers"]) == 1
    assert data[0]["computers"][0]["id"] == computer.id
    assert len(data[0]["computers"][0]["bookings"]) == 1
    assert data[0]["computers"][0]["bookings"][0]["total_price"] == 1500
