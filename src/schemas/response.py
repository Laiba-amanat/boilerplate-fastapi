"""
Unified response model definitions
Used for Swagger documentation display and response data validation
"""
from typing import Any, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    """Base response model"""
    code: int = Field(default=200, description="Response status code")
    msg: str = Field(default="OK", description="Response message")
    data: T | None = Field(default=None, description="Response data")

    @field_validator("msg", mode="before")
    @classmethod
    def set_default_msg(cls, v):
        """Set default value when msg is None"""
        return "OK" if v is None else v

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "OK",
                "data": None
            }
        }


class PageResponse(BaseModel, Generic[T]):
    """Paginated response model"""
    code: int = Field(default=200, description="Response status code")
    msg: str = Field(default="OK", description="Response message")
    data: T | None = Field(default=None, description="Response data list")
    total: int = Field(default=0, description="Total record count")
    page: int = Field(default=1, description="Current page number")
    page_size: int = Field(default=20, description="Items per page")

    @field_validator("msg", mode="before")
    @classmethod
    def set_default_msg(cls, v):
        """Set default value when msg is None"""
        return "OK" if v is None else v

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "OK",
                "data": [],
                "total": 0,
                "page": 1,
                "page_size": 20
            }
        }


class ListResponse(ResponseBase[list[T]], Generic[T]):
    """List response model (non-paginated)"""
    pass


# ============= User-related response models =============
class UserInfo(BaseModel):
    """User information model"""
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str | None = Field(default=None, description="Email")
    alias: str | None = Field(default=None, description="User alias")
    phone: str | None = Field(default=None, description="Phone number")
    is_active: bool = Field(default=True, description="Is active")
    is_superuser: bool = Field(default=False, description="Is superuser")
    dept_id: int | None = Field(default=None, description="Department ID")
    dept_name: str | None = Field(default=None, description="Department name")
    role_ids: list[int] = Field(default_factory=list, description="Role ID list")
    role_names: list[str] = Field(default_factory=list, description="Role name list")
    created_at: datetime | None = Field(default=None, description="Creation time")
    updated_at: datetime | None = Field(default=None, description="Update time")


class UserListItem(BaseModel):
    """User list item"""
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str | None = Field(default=None, description="Email")
    alias: str | None = Field(default=None, description="User alias")
    phone: str | None = Field(default=None, description="Phone number")
    is_active: bool = Field(description="Is active")
    is_superuser: bool = Field(description="Is superuser")
    dept_name: str | None = Field(default=None, description="Department name")
    role_names: list[str] = Field(default_factory=list, description="Role name list")
    created_at: datetime | None = Field(default=None, description="Creation time")


# ============= Authentication-related response models =============
class TokenInfo(BaseModel):
    """Token information"""
    access_token: str = Field(description="Access token")
    refresh_token: str = Field(description="Refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(default=14400, description="Expiration time (seconds)")
    username: str | None = Field(default=None, description="Username")


class CurrentUserInfo(BaseModel):
    """Current user information"""
    id: int = Field(description="User ID")
    username: str = Field(description="Username")
    email: str | None = Field(description="Email")
    alias: str | None = Field(description="User alias")
    is_superuser: bool = Field(description="Is superuser")
    avatar: str | None = Field(default=None, description="Avatar")
    roles: list[str] = Field(default_factory=list, description="Role list")
    permissions: list[str] = Field(default_factory=list, description="Permission list")


# ============= Basic information response models =============
class HealthInfo(BaseModel):
    """Health check information"""
    status: str = Field(default="healthy", description="Health status")
    timestamp: datetime = Field(description="Timestamp")
    environment: str = Field(description="Runtime environment")
    database: str = Field(description="Database status")


class VersionInfo(BaseModel):
    """Version information"""
    app_name: str = Field(description="Application name")
    version: str = Field(description="Version number")
    api_version: str = Field(description="API version")
    environment: str = Field(description="Runtime environment")


# ============= Menu-related response models =============
class MenuItem(BaseModel):
    """Menu item"""
    id: int = Field(description="Menu ID")
    name: str = Field(description="Menu name")
    menu_type: str = Field(description="Menu type")
    icon: str | None = Field(description="Menu icon")
    path: str | None = Field(description="Menu path")
    component: str | None = Field(description="Frontend component")
    parent_id: int | None = Field(description="Parent menu ID")
    order: int = Field(default=0, description="Order")
    is_hidden: bool = Field(default=False, description="Is hidden")
    children: list["MenuItem"] = Field(default_factory=list, description="Child menus")


# ============= Role-related response models =============
class RoleInfo(BaseModel):
    """Role information"""
    id: int = Field(description="Role ID")
    name: str = Field(description="Role name")
    desc: str | None = Field(description="Role description")
    menu_ids: list[int] = Field(default_factory=list, description="Menu ID list")
    api_ids: list[int] = Field(default_factory=list, description="API permission ID list")
    created_at: datetime | None = Field(description="Creation time")
    updated_at: datetime | None = Field(description="Update time")


class RoleListItem(BaseModel):
    """Role list item"""
    id: int = Field(description="Role ID")
    name: str = Field(description="Role name")
    desc: str | None = Field(description="Role description")
    user_count: int = Field(default=0, description="User count")
    created_at: datetime | None = Field(description="Creation time")


class RoleAuthorizedInfo(BaseModel):
    """Role permission details (includes complete menu and API information)"""
    id: int = Field(description="Role ID")
    name: str = Field(description="Role name")
    desc: str | None = Field(description="Role description")
    menus: list[MenuItem] = Field(default_factory=list, description="Menu list")
    apis: list["ApiInfo"] = Field(default_factory=list, description="API permission list")
    created_at: datetime | None = Field(description="Creation time")
    updated_at: datetime | None = Field(description="Update time")


# ============= Department-related response models =============
class DeptInfo(BaseModel):
    """Department information"""
    id: int = Field(description="Department ID")
    name: str = Field(description="Department name")
    desc: str | None = Field(description="Department description")
    parent_id: int | None = Field(description="Parent department ID")
    order: int = Field(default=0, description="Order")
    is_deleted: bool = Field(default=False, description="Is deleted")
    children: list["DeptInfo"] = Field(default_factory=list, description="Child departments")


# ============= API permission-related response models =============
class ApiInfo(BaseModel):
    """API permission information"""
    id: int = Field(description="API ID")
    path: str = Field(description="API path")
    method: str = Field(description="Request method")
    summary: str | None = Field(description="API description")
    tags: str | None = Field(description="API tags")


# ============= Audit log-related response models =============
class AuditLogItem(BaseModel):
    """Audit log item"""
    id: int = Field(description="Log ID")
    user_id: int | None = Field(description="User ID")
    username: str | None = Field(description="Username")
    module: str | None = Field(description="Function module")
    summary: str | None = Field(description="Operation description")
    method: str = Field(description="Request method")
    path: str = Field(description="Request path")
    status: int = Field(description="Response status code")
    response_time: float = Field(description="Response time (milliseconds)")
    ip: str | None = Field(description="IP address")
    created_at: datetime | None = Field(description="Creation time")


# Recursive model updates
MenuItem.model_rebuild()
DeptInfo.model_rebuild()
RoleAuthorizedInfo.model_rebuild()


# ============= Type aliases (for convenience) =============
# User-related
UserListResponse = PageResponse[list[UserListItem]]
UserDetailResponse = ResponseBase[UserInfo]
UserCreateResponse = ResponseBase[None]
UserUpdateResponse = ResponseBase[None]
UserDeleteResponse = ResponseBase[None]

# Authentication-related
TokenResponse = ResponseBase[TokenInfo]
CurrentUserResponse = ResponseBase[CurrentUserInfo]
HealthResponse = ResponseBase[HealthInfo]
VersionResponse = ResponseBase[VersionInfo]

# Menu-related
MenuListResponse = ResponseBase[list[MenuItem]]
MenuDetailResponse = ResponseBase[MenuItem]

# Role-related
RoleListResponse = PageResponse[list[RoleListItem]]
RoleDetailResponse = ResponseBase[RoleInfo]
RoleAuthorizedResponse = ResponseBase[RoleAuthorizedInfo]

# Department-related
DeptListResponse = ResponseBase[list[DeptInfo]]
DeptDetailResponse = ResponseBase[DeptInfo]

# API permission-related
ApiListResponse = PageResponse[list[ApiInfo]]

# Audit log-related
AuditLogListResponse = PageResponse[list[AuditLogItem]]