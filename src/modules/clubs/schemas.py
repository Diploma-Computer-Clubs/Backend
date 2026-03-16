from pydantic import BaseModel, Field
from typing import List

class SPromoItem(BaseModel):
    title: str = Field(..., description="Акция 3 + 2")
    value: str = Field(..., description="1000 тг")

class SClubCreate(BaseModel):
    name: str = Field(..., description="Name of club")
    address: str = Field(..., description="Address of club")
    promos: List[SPromoItem] = Field(default=[], description="Список акций клуба")
    description: str = Field(..., description="description of club")
    rating: float = Field(..., description="rating of club")
    city_id: int = Field(..., description="city id of club")
    owner_id: int = Field(..., description="owner id of club")