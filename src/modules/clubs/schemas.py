from pydantic import BaseModel, Field
from typing import List

class SPromoItem(BaseModel):
    title: str = Field(..., description="Акция 3 + 2")
    value: str = Field(..., description="1000 тг")

class SClubCreate(BaseModel):
    name: str = Field(..., description="Name of club")
    address: str = Field(..., description="Address of club")
    image_url: str = Field(..., description="Image url of club")
    image_price_url: str
    promos: List[SPromoItem] = Field(default=[], description="List of promos")
    description: str = Field(..., description="Description of club")
    rating: float = Field(..., description="Rating of club", ge=0, le=5)
    city_id: int = Field(..., description="City id of club")
    city_name: str = Field(..., description="City name of club")
    owner_id: int = Field(..., description="Owner id of club")

class SClubChange(BaseModel):
    id: int
    name: str
    address: str
    image_url: str
    image_price_url: str
    promos: List[SPromoItem]
    description: str
    city_id: int

class SClubMainInfo(BaseModel):
    id: int
    name: str
    address: str
    image_url: str
    image_price_url: str
    promos: List[SPromoItem]
    rating: float

class SClubMap(BaseModel):
    id: int
    name: str
    image_url: str
    latitude: float
    longitude: float