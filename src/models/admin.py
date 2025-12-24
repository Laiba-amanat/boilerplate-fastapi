from tortoise import fields

from schemas.menus import MenuType

from .base import BaseModel, TimestampMixin
from .enums import MethodType


class User(BaseModel, TimestampMixin):
    username = fields.CharField(
        max_length=20, unique=True, description="Username", index=True
    )
    alias = fields.CharField(max_length=30, null=True, description="Name", index=True)
    email = fields.CharField(
        max_length=255, unique=True, description="Email", index=True
    )
    phone = fields.CharField(max_length=20, null=True, description="Phone", index=True)
    password = fields.CharField(max_length=128, null=True, description="Password")
    is_active = fields.BooleanField(default=True, description="Is active", index=True)
    is_superuser = fields.BooleanField(
        default=False, description="Is superuser", index=True
    )
    last_login = fields.DatetimeField(null=True, description="Last login time", index=True)
    roles = fields.ManyToManyField("models.Role", related_name="user_roles")
    dept_id = fields.IntField(null=True, description="Department ID", index=True)

    class Meta:
        table = "user"


class Role(BaseModel, TimestampMixin):
    name = fields.CharField(
        max_length=20, unique=True, description="Role name", index=True
    )
    desc = fields.CharField(max_length=500, null=True, description="Role description")
    menus = fields.ManyToManyField("models.Menu", related_name="role_menus")
    apis = fields.ManyToManyField("models.Api", related_name="role_apis")

    class Meta:
        table = "role"


class Api(BaseModel, TimestampMixin):
    path = fields.CharField(max_length=100, description="API path", index=True)
    method = fields.CharEnumField(MethodType, description="Request method", index=True)
    summary = fields.CharField(max_length=500, description="Request summary", index=True)
    tags = fields.CharField(max_length=100, description="API tags", index=True)

    class Meta:
        table = "api"


class Menu(BaseModel, TimestampMixin):
    name = fields.CharField(max_length=20, description="Menu name", index=True)
    remark = fields.JSONField(null=True, description="Reserved field")
    menu_type = fields.CharEnumField(MenuType, null=True, description="Menu type")
    icon = fields.CharField(max_length=100, null=True, description="Menu icon")
    path = fields.CharField(max_length=100, description="Menu path", index=True)
    order = fields.IntField(default=0, description="Order", index=True)
    parent_id = fields.IntField(default=0, description="Parent menu ID", index=True)
    is_hidden = fields.BooleanField(default=False, description="Is hidden")
    component = fields.CharField(max_length=100, description="Component")
    keepalive = fields.BooleanField(default=True, description="Keep alive")
    redirect = fields.CharField(max_length=100, null=True, description="Redirect")

    class Meta:
        table = "menu"


class Dept(BaseModel, TimestampMixin):
    name = fields.CharField(
        max_length=20, unique=True, description="Department name", index=True
    )
    desc = fields.CharField(max_length=500, null=True, description="Description")
    is_deleted = fields.BooleanField(
        default=False, description="Soft delete flag", index=True
    )
    order = fields.IntField(default=0, description="Order", index=True)
    parent_id = fields.IntField(
        default=0, max_length=10, description="Parent department ID", index=True
    )

    class Meta:
        table = "dept"


class DeptClosure(BaseModel, TimestampMixin):
    ancestor = fields.IntField(description="Ancestor", index=True)
    descendant = fields.IntField(description="Descendant", index=True)
    level = fields.IntField(default=0, description="Depth", index=True)


class AuditLog(BaseModel, TimestampMixin):
    user_id = fields.IntField(description="User ID", index=True)
    username = fields.CharField(
        max_length=64, default="", description="Username", index=True
    )
    module = fields.CharField(
        max_length=64, default="", description="Function module", index=True
    )
    summary = fields.CharField(
        max_length=128, default="", description="Request description", index=True
    )
    method = fields.CharField(
        max_length=10, default="", description="Request method", index=True
    )
    path = fields.CharField(
        max_length=255, default="", description="Request path", index=True
    )
    status = fields.IntField(default=-1, description="Status code", index=True)
    response_time = fields.IntField(
        default=0, description="Response time (ms)", index=True
    )
    request_args = fields.JSONField(null=True, description="Request parameters")
    response_body = fields.JSONField(null=True, description="Response data")

    class Meta:
        table = "audit_log"


class FileMapping(BaseModel, TimestampMixin):
    """File mapping model - manages mapping relationships between file IDs and file information"""

    file_id = fields.CharField(
        max_length=255, unique=True, description="File ID", index=True
    )
    original_filename = fields.CharField(max_length=255, description="Original filename")
    file_type = fields.CharField(max_length=50, description="File type")
    file_size = fields.BigIntField(null=True, description="File size (bytes)")
    upload_user_id = fields.IntField(description="Upload user ID", index=True)
    file_path = fields.CharField(max_length=500, null=True, description="Local file path")

    class Meta:
        table = "file_mapping"
