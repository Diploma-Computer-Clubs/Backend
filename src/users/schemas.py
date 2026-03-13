import re

from pydantic import BaseModel, Field, validator, ConfigDict
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class SUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    phone_number: str = Field(..., description="Phone number have to be in int-nal format, start from '+'")
    full_name: str = Field(..., min_length=1, max_length=50, description="Name, from 1 to 50 characters")
    password_hash: str = Field(..., min_length=8, max_length = 128, description="hashed password")
    role: Role = Field(..., description="Role of user")
    city_id: int = Field(..., description="City_id of the user")

    @validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Phone number must start from "+" and contains from 1 to 15 digits')
        return value

class SUserGetData(BaseModel):
    phone_number: str
    full_name: str
    city: str = Field(..., validation_alias="city.city")

class SUserAuth(BaseModel):
    phone_number: str = Field(..., description="Phone number have to be in int-nal format, start from '+'")
    password_hash: str = Field(..., min_length=8, max_length=128, description="At least 8 characters long")
