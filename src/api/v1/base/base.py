import locale
import os
import platform
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi import extension as slowapi_extension
from slowapi.util import get_remote_address
from starlette.config import Config as StarletteConfig

from core.ctx import CTX_USER_ID
from core.dependency import DependAuth
from models.admin import User
from repositories.user import user_repository
from schemas.base import Fail, Success
from schemas.login import (
    CredentialsSchema,
    JWTOut,
    RefreshTokenRequest,
    TokenRefreshOut,
)
from schemas.response import CurrentUserResponse, TokenResponse
from settings import settings
from utils.jwt import create_token_pair, verify_token

class AdaptiveEnvConfig(StarletteConfig):
    def _read_file(self, file_name):
        encodings = ["utf-8", "utf-8-sig"]
        preferred = locale.getpreferredencoding(do_setlocale=False)
        if preferred and preferred.lower() not in (e.lower() for e in encodings):
            encodings.append(preferred)
        encodings.append("latin-1")  # final fallback to avoid UnicodeDecodeError

        last_error: UnicodeDecodeError | None = None
        for encoding in encodings:
            try:
                file_values: dict[str, str] = {}
                with open(file_name, encoding=encoding) as input_file:
                    for line in input_file.readlines():
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip("\"'")
                            file_values[key] = value
                return file_values
            except UnicodeDecodeError as exc:
                last_error = exc
        if last_error:
            raise last_error
        return {}


if getattr(slowapi_extension.Config, "__name__", "") != "AdaptiveEnvConfig":
    slowapi_extension.Config = AdaptiveEnvConfig

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


def apply_rate_limit(rate="5/minute"):
    """Apply rate limit decorator based on environment"""

    def decorator(func):

        if os.getenv("TESTING", "false").lower() == "true":
            return func  # Testing environment does not apply rate limiting
        return limiter.limit(rate)(func)

    return decorator


@router.post("/access_token", summary="Get token", response_model=TokenResponse)
@apply_rate_limit()
async def login_access_token(request: Request, credentials: CredentialsSchema):
    user: User = await user_repository.authenticate(credentials)
    await user_repository.update_last_login(user.id)

    # Create access token and refresh token
    access_token, refresh_token = create_token_pair(user_id=user.id)

    data = JWTOut(
        access_token=access_token,
        refresh_token=refresh_token,
        username=user.username,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return Success(data=data.model_dump())


@router.post("/refresh_token", summary="Refresh token", response_model=TokenResponse)
@apply_rate_limit("10/minute")
async def refresh_access_token(request: Request, refresh_request: RefreshTokenRequest):
    """
    Use refresh token to get new access token and refresh token
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_request.refresh_token, token_type="refresh")

        # Verify user still exists and is active
        user = await user_repository.get(id=payload.user_id)
        if not user or not user.is_active:
            return Fail(code=401, msg="User does not exist or has been disabled")

        # Create new token pair
        access_token, refresh_token = create_token_pair(user_id=user.id)

        data = TokenRefreshOut(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return Success(data=data.model_dump())

    except Exception as exc:  # noqa: BLE001 - propagate as HTTP error for clarity
        raise HTTPException(status_code=401, detail="Token is invalid or expired") from exc


@router.get("/userinfo", summary="Get user information", response_model=CurrentUserResponse)
async def get_userinfo(current_user: User = DependAuth):
    user_id = CTX_USER_ID.get()
    user_obj = await user_repository.get(id=user_id)
    user_dict = await user_obj.to_dict()
    return Success(data=user_dict)


@router.get("/health", summary="Health check")
async def health_check():
    """System health check"""

    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "service": settings.PROJECT_NAME,
        "database": "connected",
    }


@router.get("/version", summary="Version information")
async def get_version():
    """Get API version information"""

    return {
        "version": settings.VERSION,
        "app_title": settings.APP_TITLE,
        "project_name": settings.PROJECT_NAME,
        "build": os.getenv("APP_BUILD", "dev"),
        "commit": os.getenv("GIT_COMMIT", "unknown"),
        "python_version": platform.python_version(),
    }


# @router.get("/usermenu", summary="Get user menu", dependencies=[DependAuth])
# async def get_user_menu():
#     user_id = CTX_USER_ID.get()
#     user_obj = await User.filter(id=user_id).first()
#     menus: list[Menu] = []
#     if user_obj.is_superuser:
#         menus = await Menu.all()
#     else:
#         role_objs: list[Role] = await user_obj.roles
#         for role_obj in role_objs:
#             menu = await role_obj.menus
#             menus.extend(menu)
#         menus = list(set(menus))
#     parent_menus: list[Menu] = []
#     for menu in menus:
#         if menu.parent_id == 0:
#             parent_menus.append(menu)
#     res = []
#     for parent_menu in parent_menus:
#         parent_menu_dict = await parent_menu.to_dict()
#         parent_menu_dict["children"] = []
#         for menu in menus:
#             if menu.parent_id == parent_menu.id:
#                 parent_menu_dict["children"].append(await menu.to_dict())
#         res.append(parent_menu_dict)
#     return Success(data=res)


# @router.get("/userapi", summary="Get user API", dependencies=[DependAuth])
# async def get_user_api():
#     user_id = CTX_USER_ID.get()
#     user_obj = await User.filter(id=user_id).first()
#     if user_obj.is_superuser:
#         api_objs: list[Api] = await Api.all()
#         apis = [api.method.lower() + api.path for api in api_objs]
#         return Success(data=apis)
#     role_objs: list[Role] = await user_obj.roles
#     apis = []
#     for role_obj in role_objs:
#         api_objs: list[Api] = await role_obj.apis
#         apis.extend([api.method.lower() + api.path for api in api_objs])
#     apis = list(set(apis))
#     return Success(data=apis)


# @router.post("/update_password", summary="Update password", dependencies=[DependAuth])
# async def update_user_password(req_in: UpdatePassword):
#     user_id = CTX_USER_ID.get()
#     user = await user_controller.get(user_id)
#     verified = verify_password(req_in.old_password, user.password)
#     if not verified:
#         return Fail(msg="Old password verification failed!")
#     user.password = get_password_hash(req_in.new_password)
#     await user.save()
#     return Success(msg="Password updated successfully")
