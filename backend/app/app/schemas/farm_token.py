from typing import Optional

from app.schemas.api_model import APIModel


# Farm Token Models
class FarmTokenBase(APIModel):
    access_token: Optional[str] = None
    expires_in: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[float] = None


class FarmTokenCreate(FarmTokenBase):
    farm_id: int
    pass


class FarmToken(FarmTokenBase):
    id: int


class FarmTokenUpdate(FarmToken):
    pass


class FarmAuthorizationParams(APIModel):
    grant_type: str
    code: str
    state: str
    client_id: str
    client_secret: Optional[str]
    redirect_uri: Optional[str]
    scope: str
