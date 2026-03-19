from pydantic import BaseModel, Field
from typing import List

class SPromoItem(BaseModel):
    title: str = Field(..., description="Акция 3 + 2")
    value: str = Field(..., description="1000 тг")

class SClubCreate(BaseModel):
    name: str = Field(..., description="Name of club")
    address: str = Field(..., description="Address of club")
    image_url: str = Field(..., description="Image url of club")
    promos: List[SPromoItem] = Field(default=[], description="List of promos")
    description: str = Field(..., description="Description of club")
    rating: float = Field(..., description="Rating of club", ge=0, le=5)
    city_id: int = Field(..., description="City id of club")
    owner_id: int = Field(..., description="Owner id of club")
    latitude: float | None = None
    longitude: float | None = None

class SClubMainInfo(BaseModel):
    name: str
    address: str
    image_url: str
    promos: List[SPromoItem]
    rating: float

class SClubMap(BaseModel):
    name: str
    image_url: str
    latitude: float
    longitude: float