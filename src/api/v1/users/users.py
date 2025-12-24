from fastapi import APIRouter, Body, Query

from schemas.response import (
    ResponseBase,
    UserCreateResponse,
    UserDeleteResponse,
    UserDetailResponse,
    UserListResponse,
    UserUpdateResponse,
)
from schemas.users import UserCreate, UserUpdate
from services.user_service import user_service

router = APIRouter()


@router.get("/list", summary="Get user list", response_model=UserListResponse)
async def list_user(
    page: int = Query(1, description="Page number"),
    page_size: int = Query(10, description="Items per page"),
    username: str = Query("", description="Username for search"),
    email: str = Query("", description="Email address"),
    dept_id: int = Query(None, description="Department ID"),
):
    result = await user_service.get_user_list(
        page=page,
        page_size=page_size,
        username=username,
        email=email,
        dept_id=dept_id,
    )
    return result


@router.get("/get", summary="Get user", response_model=UserDetailResponse)
async def get_user(
    user_id: int = Query(..., description="User ID"),
):
    result = await user_service.get_user_detail(user_id)
    return result


@router.post("/create", summary="Create user", response_model=UserCreateResponse)
async def create_user(
    user_in: UserCreate,
):
    result = await user_service.create_user(user_in)
    return result


@router.post("/update", summary="Update user", response_model=UserUpdateResponse)
async def update_user(
    user_in: UserUpdate,
):
    result = await user_service.update_user(user_in)
    return result


@router.delete("/delete", summary="Delete user", response_model=UserDeleteResponse)
async def delete_user(
    user_id: int = Query(..., description="User ID"),
):
    result = await user_service.delete_user(user_id)
    return result


@router.post("/reset_password", summary="Reset password", response_model=ResponseBase[None])
async def reset_password(user_id: int = Body(..., description="User ID", embed=True)):
    result = await user_service.reset_user_password(user_id)
    return result
