from typing import Optional, List

from pydantic import Field, ConfigDict, field_validator, BaseModel
from src.shared.schemas.schemas import SUserBase, SUserPassword, Role

class SUser(SUserBase, SUserPassword):
    model_config = ConfigDict(from_attributes=True)
    full_name: str = Field(..., min_length=1, max_length=50)
    role: Role = Field(default=Role.user)
    city_id: int = Field(..., description="City_id of the user")

class SUserGetData(SUserBase):
    model_config = ConfigDict(from_attributes=True)
    full_name: str
    role: Role
    city: str = Field(..., description="Название города")
    club_ids: List[int] = []
    reputation: int
    staff_role: Optional[str] = None
    owner: Optional[str] = "None"

    @field_validator("city", mode="before")
    @classmethod
    def get_city_name(cls, v):
        if hasattr(v, 'city'):
            return v.city
        return v


class SUserPostData(BaseModel):
    city_id: int
    full_name: str

class SUserVerify(SUserBase):
    code: str = Field(..., description="verifying code")

class SUserPhoneAuth(SUserBase):
    pass