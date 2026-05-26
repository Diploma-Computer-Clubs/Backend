import pytest

from src.shared.schemas.schemas import Role


pytestmark = pytest.mark.asyncio


async def test_add_city_and_list_cities(client):
    response = await client.post("/cities/", json={"city": "Astana"})

    assert response.status_code == 200
    assert response.json()["message"] == "City successfully added"

    list_response = await client.get("/cities/")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["city"] == "Astana"


async def test_update_city_requires_super_admin_and_updates_city_data(client, factory):
    user_city = await factory.create_city(city_name="UserCity")
    admin = await factory.create_user(role=Role.admin, city_id=user_city.id)
    regular_user = await factory.create_user(city_id=user_city.id)
    city = await factory.create_city(city_name="Astana")
    payload = {"id": city.id, "city": "Almaty"}

    forbidden_response = await client.patch(
        f"/cities/{city.id}",
        json=payload,
        headers=factory.auth_headers(factory.access_token(regular_user.id)),
    )
    assert forbidden_response.status_code == 403

    update_response = await client.patch(
        f"/cities/{city.id}",
        json=payload,
        headers=factory.auth_headers(factory.access_token(admin.id)),
    )
    assert update_response.status_code == 200
    assert update_response.json()["message"] == "City updated successfully"

    list_response = await client.get("/cities/")
    assert list_response.status_code == 200
    assert any(item["id"] == city.id and item["city"] == "Almaty" for item in list_response.json())

    coordinates_response = await client.get(f"/cities/{city.id}/coordinates")
    assert coordinates_response.status_code == 200
    coordinates = coordinates_response.json()
    assert coordinates["latitude"] is not None
    assert coordinates["longitude"] is not None


async def test_delete_city_requires_super_admin(client, factory):
    user_city = await factory.create_city(city_name="UserCity")
    admin = await factory.create_user(role=Role.admin, city_id=user_city.id)
    regular_user = await factory.create_user(city_id=user_city.id)
    city = await factory.create_city()

    forbidden_response = await client.delete(
        f"/cities/{city.id}",
        headers=factory.auth_headers(factory.access_token(regular_user.id)),
    )
    assert forbidden_response.status_code == 403

    delete_response = await client.delete(
        f"/cities/{city.id}",
        headers=factory.auth_headers(factory.access_token(admin.id)),
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "City deleted successfully"

    list_response = await client.get("/cities/")
    assert list_response.status_code == 200
    assert all(item["id"] != city.id for item in list_response.json())
