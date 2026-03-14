from pydantic import Field, ConfigDict, field_validator
from src.shared.schemas.users import SUserBase, SUserPassword, Role

class SUser(SUserBase, SUserPassword):
    model_config = ConfigDict(from_attributes=True)
    full_name: str = Field(..., min_length=1, max_length=50)
    role: Role = Field(default=Role.user)
    city_id: int = Field(..., description="City_id of the user")

class SUserGetData(SUserBase):
    model_config = ConfigDict(from_attributes=True)
    full_name: str
    city: str = Field(..., description="Название города")

    @field_validator("city", mode="before")
    @classmethod
    def get_city_name(cls, v):
        if hasattr(v, 'city'):
            return v.city
        return v