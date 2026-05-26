import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_owner_can_create_package_and_calculate_bulk_price(client, factory):
    city = await factory.create_city()
    owner = await factory.create_user(role=Role.owner, city_id=city.id)
    club = await factory.create_club(owner_id=owner.id, city_id=city.id)
    zone = await factory.create_zone(club_id=club.id)
    start_time, end_time = factory.booking_window(hours_from_now=4, duration_hours=2)

    create_response = await client.post(
        "/pricing/",
        params={"club_id": club.id},
        headers=factory.auth_headers(factory.access_token(owner.id)),
        json={
            "name": "Base hour",
            "duration": 1,
            "price": 500,
            "is_package": False,
            "zone_id": zone.id,
        },
    )
    assert create_response.status_code == 200

    calculate_response = await client.post(
        "/pricing/calculate",
        json=[
            {
                "items": [{"zone_id": zone.id, "count": 2}],
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }
        ],
    )

    assert calculate_response.status_code == 200
    assert calculate_response.json()["total_amount"] == 2000
