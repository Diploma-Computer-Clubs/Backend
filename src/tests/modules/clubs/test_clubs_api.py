from datetime import datetime, timedelta

import pytest

from src.modules.bookings.dao import BookingDAO
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


async def test_owner_can_export_club_statistics_to_excel(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id, full_name="Owner Name")
    user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id, name="Cyber Arena Stats")
    zone = await factory.create_zone(club_id=club.id, name="VIP")
    first_computer = await factory.create_computer(zone_id=zone.id, number=71)
    second_computer = await factory.create_computer(zone_id=zone.id, number=72)
    await factory.create_package(zone_id=zone.id, name="Base hour", duration=1, price=500, is_package=False)
    await factory.create_package(zone_id=zone.id, name="Night package", duration=2, price=900, is_package=True)
    start_time = (datetime.now() - timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=2)
    first_booking = await factory.create_booking(
        user_id=user.id,
        club_id=club.id,
        zone_id=zone.id,
        computer_id=first_computer.id,
        start_time=start_time,
        end_time=end_time,
        total_price=900,
    )
    second_booking = await factory.create_booking(
        user_id=user.id,
        club_id=club.id,
        zone_id=zone.id,
        computer_id=first_computer.id,
        start_time=end_time + timedelta(hours=1),
        end_time=end_time + timedelta(hours=2),
        total_price=500,
    )
    third_booking = await factory.create_booking(
        user_id=user.id,
        club_id=club.id,
        zone_id=zone.id,
        computer_id=second_computer.id,
        start_time=end_time + timedelta(hours=3),
        end_time=end_time + timedelta(hours=4),
        total_price=500,
    )
    await BookingDAO.update_check_in_status(first_booking.id, True)
    await BookingDAO.update_check_in_status(second_booking.id, True)
    await BookingDAO.update_check_in_status(third_booking.id, True)

    response = await client.post(
        f"/clubs/{club.id}/statistics/export",
        headers=factory.auth_headers(factory.access_token(owner.id)),
        json={
            "start_date": start_time.date().isoformat(),
            "end_date": start_time.date().isoformat(),
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.ms-excel"
    assert "attachment;" in response.headers["content-disposition"]

    content = response.content.decode("utf-8")
    assert "Cyber Arena Stats" in content
    assert "Owner Name" in content
    assert "Payment type price" in content
    assert "VIP" in content
    assert "Computer 71" not in content
    assert ">71<" in content
    assert ">72<" in content
    assert "Zone total amount" in content
    assert "Total amount" in content
    assert "Night package" in content
    assert "Base hour" in content
    assert ">900<" in content
    assert ">500<" in content
    assert ">1900.0<" in content
    assert content.count(">1400.0<") == 1
    assert content.count(">1900.0<") == 2
