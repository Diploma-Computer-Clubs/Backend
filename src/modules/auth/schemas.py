from pydantic import Field

from src.shared.schemas.schemas import SUserBase, SUserPassword

class SUserAuth(SUserBase, SUserPassword):
    pass

