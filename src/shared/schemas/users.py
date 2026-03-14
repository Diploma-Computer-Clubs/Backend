import re
from pydantic import BaseModel, Field, validator
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"

class SUserBase(BaseModel):
    phone_number: str = Field(..., description="Phone number in int-nal format, starts with '+'")

    @validator("phone_number")
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Phone number must start with "+" and contain 1-15 digits')
        return value

class SUserPassword(BaseModel):
    password: str = Field(..., min_length=8, max_length=128, description="Password")