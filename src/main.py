from fastapi import FastAPI
from src.modules.users.router import router as router_users
from src.modules.auth.router import router as router_auth
from src.modules.cities.router import router as cities_router
from src.modules.users.model import User
from src.modules.cities.model import City
from src.modules.clubs.model import Club
from src.modules.zones.model import Zone
from src.modules.computers.model import Computer
from src.modules.bookings.model import Booking

app = FastAPI()

@app.get("/")
async def root():

    return {"Success"}

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(cities_router)