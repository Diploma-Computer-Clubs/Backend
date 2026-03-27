from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from src.modules.clubs.schemas import SClubCreate, SClubChange
from src.modules.clubs.dao import ClubDAO
from src.shared.service.coordinate_service import CoordinatesService


class ClubService:

    @classmethod
    async def create_club(cls, club_info: SClubCreate, user_id: int):
        address = club_info.city_name + " , " +club_info.address
        lat, lon = await CoordinatesService.get_coordinates_2gis(address)
        club_data = club_info.model_dump()
        club_data.pop("city_name", None)
        club_data["latitude"] = lat
        club_data["longitude"] = lon
        club_data["owner_id"] = user_id
        try:
            new_city = await ClubDAO.add(**club_data)
            return new_city

        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail=f"'{club_info.name}' invalid data",
            )
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Invalid error"
            )

    @classmethod
    async def get_clubs(cls):
        result = await ClubDAO.find()
        return result

    @classmethod
    async def get_club(cls, club_id: int):
        result = await ClubDAO.find_one_or_none_by_id(club_id)
        return result

    @classmethod
    async def get_clubs_by_city(cls, city_id: int):
        result = await ClubDAO.find_full_data(city_id=city_id)
        return result

    @classmethod
    async def get_clubs_count(cls, city_id: int):
        return await ClubDAO.count_by_city(city_id)

    @classmethod
    async def delete_clubs(cls, club_id: int, user_id: int):
        owner_id = await ClubService.get_club(club_id)
        if owner_id.owner_id == user_id:
            return await ClubDAO.delete(id=club_id)
        raise HTTPException(status_code=403, detail=f"User don't have an access to the club or club not found")

    @classmethod
    async def update_club(cls, club_info: SClubChange, user_id: int):
        address = club_info.city_name + " , " + club_info.address
        lat, lon = await CoordinatesService.get_coordinates_2gis(address)
        club_data = club_info.model_dump()
        club_data.pop("city_name", None)
        club_data["latitude"] = lat
        club_data["longitude"] = lon
        owner_id = await ClubService.get_club(club_info.id)
        if owner_id.owner_id == user_id:
            club_data.pop("id", None)
            return await ClubDAO.update(filter_by={"id": club_info.id}, **club_data, updated_at=func.now())
        raise HTTPException(status_code=403, detail=f"User don't have an access to the '{club_info.name}' club")

    @classmethod
    async def get_club_min_price(cls, club_id: int):
        club = await cls.get_club(club_id)
        if not club:
            return None

        min_price = await ClubDAO.get_min_price_by_club(club_id)
        return min_price if min_price is not None else 0