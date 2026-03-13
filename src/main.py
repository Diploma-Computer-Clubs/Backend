from fastapi import FastAPI
from src.users.router import router as router_users
from src.users.router_auth import router as router_auth
from src.cities.router import router as cities_router

app = FastAPI()

@app.get("/")
async def root():

    return {"Success"}

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(cities_router)