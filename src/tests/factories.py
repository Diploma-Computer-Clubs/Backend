from __future__ import annotations

from datetime import datetime, timedelta, time
from itertools import count
from uuid import uuid4

from src.modules.bookings.model import Booking
from src.modules.cities.model import City
from src.modules.club_staff.model import ClubStaff
from src.modules.clubs.model import Club
from src.modules.computers.model import Computer
from src.modules.pricing.model import ZonePackage
from src.modules.users.model import User
from src.modules.zones.model import Zone
from src.shared.auth.jwt import create_access_token, create_refresh_token
from src.shared.configurations.database import async_session_maker
from src.shared.schemas.schemas import Role
from src.shared.utils.auth_utils import get_password_hash


class TestFactory:
    _phone_counter = count(77000000000)

    @staticmethod
    def auth_headers(token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def access_token(user_id: int) -> str:
        return create_access_token({"sub": str(user_id)})

    @staticmethod
    def refresh_token(user_id: int) -> str:
        return create_refresh_token({"sub": str(user_id)})

    @classmethod
    def unique_phone(cls) -> str:
        return f"+{next(cls._phone_counter)}"

    @staticmethod
    def unique_text(prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"

    @staticmethod
    def booking_window(hours_from_now: int = 2, duration_hours: int = 2) -> tuple[datetime, datetime]:
        start = (datetime.now() + timedelta(hours=hours_from_now)).replace(microsecond=0)
        end = start + timedelta(hours=duration_hours)
        return start, end

    async def create_city(
        self,
        city_name: str | None = None,
        latitude: float = 51.1694,
        longitude: float = 71.4491,
    ) -> City:
        async with async_session_maker() as session:
            city = City(
                city=city_name or self.unique_text("City"),
                latitude=latitude,
                longitude=longitude,
            )
            session.add(city)
            await session.commit()
            await session.refresh(city)
            return city

    async def create_user(
        self,
        *,
        phone_number: str | None = None,
        password: str = "Password123!",
        full_name: str = "Test User",
        role: Role = Role.user,
        city_id: int | None = None,
    ) -> User:
        if city_id is None:
            city_id = (await self.create_city()).id

        async with async_session_maker() as session:
            user = User(
                phone_number=phone_number or self.unique_phone(),
                password=get_password_hash(password),
                full_name=full_name,
                role=role,
                city_id=city_id,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def create_club(
        self,
        *,
        owner_id: int,
        city_id: int,
        name: str | None = None,
        address: str | None = None,
        image_url: str = "https://example.com/club.png",
        description: str = "Club description",
        rating: float = 5.0,
        latitude: float = 51.1694,
        longitude: float = 71.4491,
    ) -> Club:
        async with async_session_maker() as session:
            club = Club(
                name=name or self.unique_text("Club"),
                address=address or self.unique_text("Address"),
                image_url=image_url,
                image_price_url=None,
                img_background=None,
                promos=[],
                description=description,
                rating=rating,
                latitude=latitude,
                longitude=longitude,
                owner_id=owner_id,
                city_id=city_id,
            )
            session.add(club)
            await session.commit()
            await session.refresh(club)
            return club

    async def create_zone(
        self,
        *,
        club_id: int,
        name: str = "Standard",
        cost: int = 500,
        cpu: str = "Ryzen 5",
        gpu: str = "RTX 4060",
        ram: str = "16GB",
        ssd: str = "1TB",
        monitor: str = "144Hz",
        x: float | None = 10.0,
        y: float | None = 20.0,
    ) -> Zone:
        async with async_session_maker() as session:
            zone = Zone(
                name=name,
                cost=cost,
                cpu=cpu,
                gpu=gpu,
                ram=ram,
                ssd=ssd,
                monitor=monitor,
                x=x,
                y=y,
                club_id=club_id,
            )
            session.add(zone)
            await session.commit()
            await session.refresh(zone)
            return zone

    async def create_computer(
        self,
        *,
        zone_id: int,
        number: int = 1,
        specification: str = "Ryzen 5 / RTX 4060 / 16GB",
        is_active: bool = True,
        x: float | None = 1.0,
        y: float | None = 1.0,
    ) -> Computer:
        async with async_session_maker() as session:
            computer = Computer(
                number=number,
                specification=specification,
                is_active=is_active,
                x=x,
                y=y,
                zone_id=zone_id,
            )
            session.add(computer)
            await session.commit()
            await session.refresh(computer)
            return computer

    async def create_booking(
        self,
        *,
        user_id: int,
        club_id: int,
        zone_id: int,
        computer_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        total_price: int = 1000,
    ) -> Booking:
        start_time = start_time or self.booking_window()[0]
        end_time = end_time or (start_time + timedelta(hours=2))

        async with async_session_maker() as session:
            booking = Booking(
                user_id=user_id,
                club_id=club_id,
                zone_id=zone_id,
                computer_id=computer_id,
                start_time=start_time,
                end_time=end_time,
                total_price=total_price,
            )
            session.add(booking)
            await session.commit()
            await session.refresh(booking)
            return booking

    async def create_staff_member(
        self,
        *,
        club_id: int,
        user_id: int,
        staff_role: str = "admin",
    ) -> ClubStaff:
        async with async_session_maker() as session:
            staff = ClubStaff(club_id=club_id, user_id=user_id, staff_role=staff_role)
            session.add(staff)
            await session.commit()
            await session.refresh(staff)
            return staff

    async def create_package(
        self,
        *,
        zone_id: int,
        name: str = "Base hour",
        start_time: time | None = None,
        end_time: time | None = None,
        duration: int = 1,
        price: int = 500,
        is_package: bool = False,
    ) -> ZonePackage:
        async with async_session_maker() as session:
            package = ZonePackage(
                name=name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                price=price,
                is_package=is_package,
                zone_id=zone_id,
            )
            session.add(package)
            await session.commit()
            await session.refresh(package)
            return package
