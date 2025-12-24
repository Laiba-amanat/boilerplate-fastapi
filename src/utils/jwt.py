from datetime import UTC, datetime, timedelta

import jwt

from schemas.login import JWTPayload
from settings.config import settings


def create_access_token(*, data: JWTPayload):
    """Create access token"""
    payload = data.model_dump().copy()
    # Ensure token_type is access
    payload["token_type"] = "access"
    encoded_jwt = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int) -> str:
    """Create refresh token"""
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = JWTPayload(
        user_id=user_id,
        exp=expire,
        token_type="refresh",
    )

    payload_dict = payload.model_dump()
    # Ensure token_type is refresh
    payload_dict["token_type"] = "refresh"

    return jwt.encode(
        payload_dict, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str, token_type: str = "access") -> JWTPayload:
    """Verify token and return payload"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        # Check token type
        if payload.get("token_type") != token_type:
            raise jwt.InvalidTokenError(f"Invalid token type. Expected {token_type}")

        return JWTPayload(**payload)

    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise jwt.InvalidTokenError("Invalid token") from e


def create_token_pair(user_id: int) -> tuple[str, str]:
    """Create access token and refresh token pair"""
    # Create access token
    access_expire = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_payload = JWTPayload(
        user_id=user_id,
        exp=access_expire,
        token_type="access",
    )
    access_token = create_access_token(data=access_payload)

    # Create refresh token
    refresh_token = create_refresh_token(user_id)

    return access_token, refresh_token
