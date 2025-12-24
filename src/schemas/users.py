import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class BaseUser(BaseModel):
    id: int
    email: EmailStr | None = None
    username: str | None = None
    is_active: bool | None = True
    is_superuser: bool | None = False
    created_at: datetime | None
    updated_at: datetime | None
    last_login: datetime | None
    roles: list | None = []


class UserCreate(BaseModel):
    email: EmailStr = Field(example="admin@qq.com")
    username: str = Field(
        example="admin",
        min_length=3,
        max_length=20,
        pattern="^[a-zA-Z0-9_]+$",
        description="Username (3-20 characters: letters, numbers, underscore)",
    )
    password: str = Field(
        example="AdminPass123",
        min_length=8,
        description="Password (at least 8 characters, containing letters and numbers)",
    )
    is_active: bool | None = True
    is_superuser: bool | None = False
    role_ids: list[int] | None = []
    dept_id: int | None = Field(0, description="Department ID")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain letters")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain numbers")

        # Optional: check special characters
        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        #     raise ValueError('Password should contain special characters')

        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        return v

    def create_dict(self):
        return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class UserUpdate(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    role_ids: list[int] | None = []
    dept_id: int | None = 0


class UpdatePassword(BaseModel):
    old_password: str = Field(description="Old password")
    new_password: str = Field(
        min_length=8, description="New password (at least 8 characters, containing letters and numbers)"
    )

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")

        if not re.search(r"[A-Za-z]", v):
            raise ValueError("New password must contain letters")

        if not re.search(r"\d", v):
            raise ValueError("New password must contain numbers")

        return v
