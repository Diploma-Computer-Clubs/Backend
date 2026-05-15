from contextlib import asynccontextmanager

import redis
from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware

from src.exception_handlers import redis_connection_error_handler, sqlalchemy_error_handler

from src.modules.users.router import router as router_users
from src.modules.auth.router import router as router_auth
from src.modules.cities.router import router as cities_router
from src.modules.clubs.router import router as clubs_router, ws_club_availability
from src.modules.media.router import router as media_router
from src.modules.zones.router import router as zones_router
from src.modules.computers.router import router as computers_router
from src.modules.bookings.router import router as bookings_router
from src.modules.pricing.router import router as pricing_router
from src.modules.club_staff.router import router as clubs_staff_router
from fastapi.staticfiles import StaticFiles

from src.shared.configurations.database import engine
from src.shared.models.model import *

from src.modules.users.model import User
from src.modules.cities.model import City
from src.modules.clubs.model import Club
from src.modules.zones.model import Zone
from src.modules.computers.model import Computer
from src.modules.bookings.model import Booking
from src.modules.pricing.model import ZonePackage
from src.modules.club_staff.model import ClubStaff


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(City.__table__.create, checkfirst=True)
        await conn.run_sync(User.__table__.create, checkfirst=True)
        await conn.run_sync(Club.__table__.create, checkfirst=True)
        await conn.run_sync(Zone.__table__.create, checkfirst=True)
        await conn.run_sync(Computer.__table__.create, checkfirst=True)
        await conn.run_sync(ZonePackage.__table__.create, checkfirst=True)
        await conn.run_sync(Booking.__table__.create, checkfirst=True)
        await conn.run_sync(ClubStaff.__table__.create, checkfirst=True)

    async with engine.connect() as conn:
        if conn.dialect.name == "postgresql":
            conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await conn.exec_driver_sql("ALTER TYPE role ADD VALUE IF NOT EXISTS 'owner'")

    yield


app = FastAPI(lifespan=lifespan)





app.include_router(router_auth)
app.include_router(router_users)
app.include_router(cities_router)
app.include_router(clubs_router)
app.include_router(media_router)
app.include_router(zones_router)
app.include_router(computers_router)
app.include_router(bookings_router)
app.include_router(pricing_router)
app.include_router(clubs_staff_router)
app.add_api_websocket_route("/{club_id}/availability/ws", ws_club_availability, name="ws_club_availability_legacy")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_exception_handler(redis.exceptions.ConnectionError, redis_connection_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

