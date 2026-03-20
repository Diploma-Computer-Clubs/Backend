from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.modules.clubs.schemas import SClubCreate, SClubChange
from src.modules.clubs.dao import ClubDAO
from src.shared.service.coordinate_service import CoordinatesService


class ClubService:

    @classmethod
    async def create_club(cls, club_info: SClubCreate):
        lat, lon = await CoordinatesService.get_coordinates_2gis(club_info.address)
        club_data = club_info.model_dump()
        club_data["latitude"] = lat
        club_data["longitude"] = lon
        try:
            new_city = await ClubDAO.add(**club_data)
            return new_city

        except IntegrityError:
            raise HTTPException(
                status_code=409,
                detail=f"Club '{club_info.name}' already exists or invalid data",
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
    async def delete_clubs(cls, club_id: int):
        return await ClubDAO.delete(id=club_id)

    @classmethod
    async def upadate_clubs(cls, club_info: SClubChange):
        return await ClubDAO.update(id=club_info.id, **club_info.model_dump())