from pydantic import BaseModel, Field

class SCityAdd(BaseModel):
    city: str = Field(..., description="City name")
    latitude: float | None = None
    longitude: float | None = None

class SCityUpdDesc(SCityAdd):
    id: int

class SCityCoordinates(BaseModel):
    latitude: float | None = None
    longitude: float | None = None