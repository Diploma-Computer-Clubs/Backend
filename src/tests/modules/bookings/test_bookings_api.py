import pytest

from src.modules.bookings.dao import BookingDAO
from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_user_can_create_booking_and_get_it_in_my_bookings(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    start_time, end_time = factory.booking_window()

    create_response = await client.post(
        "/bookings",
        headers=factory.auth_headers(factory.access_token(user.id)),
        json=[
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1200,
                "computer_id": computer.id,
                "zone_id": zone.id,
                "club_id": club.id,
            }
        ],
    )
    assert create_response.status_code == 200

    my_bookings_response = await client.get(
        "/bookings/me",
        headers=factory.auth_headers(factory.access_token(user.id)),
    )
    assert my_bookings_response.status_code == 200
    bookings = my_bookings_response.json()
    assert len(bookings) == 1
    assert bookings[0]["club"]["name"] == club.name
    assert bookings[0]["computer"]["number"] == computer.number


async def test_booking_conflict_returns_409_for_overlapping_slot(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    first_user = await factory.create_user(city_id=city.id)
    second_user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    start_time, end_time = factory.booking_window()

    first_response = await client.post(
        "/bookings",
        headers=factory.auth_headers(factory.access_token(first_user.id)),
        json=[
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1200,
                "computer_id": computer.id,
                "zone_id": zone.id,
                "club_id": club.id,
            }
        ],
    )
    assert first_response.status_code == 200

    conflict_response = await client.post(
        "/bookings",
        headers=factory.auth_headers(factory.access_token(second_user.id)),
        json=[
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1400,
                "computer_id": computer.id,
                "zone_id": zone.id,
                "club_id": club.id,
            }
        ],
    )
    assert conflict_response.status_code == 409
    assert conflict_response.json()["detail"] == "This time slot is already occupied"


async def test_owner_can_delete_booking_via_admin_endpoint_when_other_user_cannot(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    booker = await factory.create_user(city_id=city.id)
    other_user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    start_time, end_time = factory.booking_window()

    booking_response = await client.post(
        "/bookings",
        headers=factory.auth_headers(factory.access_token(booker.id)),
        json=[
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1200,
                "computer_id": computer.id,
                "zone_id": zone.id,
                "club_id": club.id,
            }
        ],
    )
    booking_id = booking_response.json()[0]["id"]

    forbidden_response = await client.delete(
        f"/bookings/{booking_id}",
        headers=factory.auth_headers(factory.access_token(other_user.id)),
    )
    assert forbidden_response.status_code == 403

    delete_response = await client.delete(
        f"/bookings/{booking_id}/admin",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(owner.id)),
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == 1

    my_bookings_response = await client.get(
        "/bookings/me",
        headers=factory.auth_headers(factory.access_token(booker.id)),
    )
    assert my_bookings_response.status_code == 200
    assert my_bookings_response.json() == []


async def test_booking_is_created_with_check_in_false_by_default(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    start_time, end_time = factory.booking_window()

    create_response = await client.post(
        "/bookings",
        headers=factory.auth_headers(factory.access_token(user.id)),
        json=[
            {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_price": 1200,
                "computer_id": computer.id,
                "zone_id": zone.id,
                "club_id": club.id,
            }
        ],
    )
    assert create_response.status_code == 200
    booking_id = create_response.json()[0]["id"]

    booking = await BookingDAO.find_one_or_none(id=booking_id)
    assert booking.is_checked_in is False


async def test_owner_can_change_booking_check_in_status(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    user = await factory.create_user(city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    computer = await factory.create_computer(zone_id=zone.id)
    booking = await factory.create_booking(
        user_id=user.id,
        club_id=club.id,
        zone_id=zone.id,
        computer_id=computer.id,
    )

    update_response = await client.patch(
        "/bookings/check-in",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(owner.id)),
        json={"booking_id": booking.id, "is_checked_in": True},
    )
    assert update_response.status_code == 200
    assert update_response.json() is True

    updated_booking = await BookingDAO.find_one_or_none(id=booking.id)
    assert updated_booking.is_checked_in is True
