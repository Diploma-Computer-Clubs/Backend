from pydantic import Field

from src.shared.schemas.schemas import SUserBase, SUserPassword

class SUserAuth(SUserBase, SUserPassword):
    pass

class SUserPhoneAuth(SUserBase):
    pass

class SUserVerify(SUserBase):
    code: str = Field(..., description="verifying code")