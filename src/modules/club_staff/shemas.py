from pydantic import BaseModel

class SClubStaffAdd(BaseModel):
    phone_number: str
    staff_role: str

class SClubStaffInfo(BaseModel):
    full_name: str
    staff_role: str

    class Config:
        from_attributes = True
