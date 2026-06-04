from pydantic import BaseModel, ConfigDict


class SClubStaffAdd(BaseModel):
    phone_number: str
    staff_role: str

class SClubStaffInfo(BaseModel):
    full_name: str
    staff_role: str

    model_config = ConfigDict(from_attributes=True)
