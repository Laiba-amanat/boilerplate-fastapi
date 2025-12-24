from datetime import datetime

from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    username: str = Field(..., description="Username", example="admin")
    password: str = Field(..., description="Password", example="Please enter the correct test password")


class JWTOut(BaseModel):
    access_token: str
    refresh_token: str
    username: str
    token_type: str = "bearer"
    expires_in: int  # Expiration time (seconds)


class JWTPayload(BaseModel):
    user_id: int
    exp: datetime
    token_type: str = "access"  # access or refresh


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class TokenRefreshOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # New access_token expiration time (seconds)
