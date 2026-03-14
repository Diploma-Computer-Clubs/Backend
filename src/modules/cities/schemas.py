from pydantic import BaseModel, Field

class SCityAdd(BaseModel):
    city: str = Field(..., description="City name to add")

class SCityUpdDesc(BaseModel):
    id: int
    city: str = Field(..., description="New city name")