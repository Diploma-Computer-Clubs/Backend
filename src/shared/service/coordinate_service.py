import httpx

from src.shared.configurations.config import settings


class CoordinatesService:

    @classmethod
    async def get_coordinates_2gis(cls, address: str):
        url = "https://catalog.api.2gis.com/3.0/items/geocode"
        params = {
            "q": address,
            "fields": "items.point",
            "key": settings.DG_API_KEY
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                data = response.json()

                result = data.get("result", {})
                items = result.get("items", [])

                if items and len(items) > 0:
                    point = items[0].get("point")
                    if point:
                        return float(point["lat"]), float(point["lon"])

                print(f"No results with address: '{address}'")

            except Exception as e:
                print(f"Backend error: {e}")

            return None, None