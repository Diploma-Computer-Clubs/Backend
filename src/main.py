import redis
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.modules.users.router import router as router_users
from src.modules.auth.router import router as router_auth
from src.modules.cities.router import router as cities_router
from src.modules.clubs.router import router as clubs_router
from src.modules.media.router import router as media_router
from src.modules.zones.router import router as zones_router
from src.modules.computers.router import router as computers_router
from src.modules.bookings.router import router as bookings_router
from fastapi.staticfiles import StaticFiles
from src.shared.models.model import *

app = FastAPI()





app.include_router(router_auth)
app.include_router(router_users)
app.include_router(cities_router)
app.include_router(clubs_router)
app.include_router(media_router)
app.include_router(zones_router)
app.include_router(computers_router)
app.include_router(bookings_router)
app.mount("/static", StaticFiles(directory="static"), name="static")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)