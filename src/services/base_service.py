from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.models import Model

from core.crud import CRUDBase
from log import logger
from models.admin import Role, User
from schemas.base import Fail, Success, SuccessExtra

T = TypeVar("T", bound=Model)


class BaseService:
    """Base service class - unified common logic"""

    def __init__(self, repository: CRUDBase):
        self.repository = repository
        self.logger = logger

    async def get_paginated_list(
        self,
        page: int = 1,
        page_size: int = 10,
        search_filters: Q | None = None,
        order: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        include_m2m: bool = False,
        transform_func: Callable | None = None,
    ) -> SuccessExtra:
        """Get paginated list - unified version

        Args:
            page: Page number
            page_size: Items per page
            search_filters: Search conditions
            order: Sort fields
            exclude_fields: Fields to exclude
            include_m2m: Whether to include many-to-many relationships
            transform_func: Data transformation function

        Returns:
            SuccessExtra: Paginated response
        """
        try:
            total, items = await self.repository.list(
                page=page,
                page_size=page_size,
                search=search_filters or Q(),
                order=order or ["-created_at"],
            )

            # Transform data
            if transform_func:
                data = await transform_func(items)
            else:
                data = [
                    await item.to_dict(
                        m2m=include_m2m, exclude_fields=exclude_fields or []
                    )
                    for item in items
                ]

            return SuccessExtra(data=data, total=total, page=page, page_size=page_size)

        except Exception as e:
            self.logger.error(f"Failed to get paginated list: {str(e)}")
            return Fail(msg="Failed to get list")

    async def get_by_id(
        self,
        item_id: int,
        exclude_fields: list[str] | None = None,
        include_m2m: bool = False,
        not_found_msg: str = "Record does not exist",
    ) -> Success:
        """Get single record by ID

        Args:
            item_id: Record ID
            exclude_fields: Fields to exclude
            include_m2m: Whether to include many-to-many relationships
            not_found_msg: Error message when not found

        Returns:
            Success: Success response
        """
        try:
            item = await self.repository.get(item_id)
            if not item:
                raise HTTPException(status_code=404, detail=not_found_msg)

            data = await item.to_dict(
                m2m=include_m2m, exclude_fields=exclude_fields or []
            )
            return Success(data=data)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get record: {str(e)}")
            return Fail(msg="Failed to get record")

    async def create_item(
        self,
        item_data: dict[str, Any],
        success_msg: str = "Created successfully",
        exclude_fields: list[str] | None = None,
    ) -> Success:
        """Create record

        Args:
            item_data: Creation data
            success_msg: Success message
            exclude_fields: Fields to exclude

        Returns:
            Success: Success response
        """
        try:
            item = await self.repository.create(item_data)
            data = await item.to_dict(exclude_fields=exclude_fields or [])
            return Success(data=data, msg=success_msg)

        except Exception as e:
            self.logger.error(f"Failed to create record: {str(e)}")
            return Fail(msg="Failed to create")

    async def update_item(
        self,
        item_id: int,
        item_data: dict[str, Any],
        success_msg: str = "Updated successfully",
        not_found_msg: str = "Record does not exist",
        exclude_fields: list[str] | None = None,
    ) -> Success:
        """Update record

        Args:
            item_id: Record ID
            item_data: Update data
            success_msg: Success message
            not_found_msg: Not found message
            exclude_fields: Fields to exclude

        Returns:
            Success: Success response
        """
        try:
            item = await self.repository.get(item_id)
            if not item:
                raise HTTPException(status_code=404, detail=not_found_msg)

            updated_item = await self.repository.update(item_id, item_data)
            data = await updated_item.to_dict(exclude_fields=exclude_fields or [])
            return Success(data=data, msg=success_msg)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to update record: {str(e)}")
            return Fail(msg="Failed to update")

    async def delete_item(
        self,
        item_id: int,
        success_msg: str = "Deleted successfully",
        not_found_msg: str = "Record does not exist",
    ) -> Success:
        """Delete record

        Args:
            item_id: Record ID
            success_msg: Success message
            not_found_msg: Not found message

        Returns:
            Success: Success response
        """
        try:
            item = await self.repository.get(item_id)
            if not item:
                raise HTTPException(status_code=404, detail=not_found_msg)

            await self.repository.remove(item_id)
            return Success(msg=success_msg)

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete record: {str(e)}")
            return Fail(msg="Failed to delete")


class PermissionService:
    """Permission service - unified permission check logic"""

    @staticmethod
    async def check_superuser(
        user: User, error_msg: str = "Insufficient permissions, superuser privileges required"
    ):
        """Check superuser permissions"""
        if not user.is_superuser:
            return Fail(code=403, msg=error_msg)
        return None

    @staticmethod
    async def get_user_agent_ids(user: User) -> set:
        """Get set of agent IDs user has permissions for"""
        if user.is_superuser:
            return set()  # Superuser has no restrictions

        roles: list[Role] = await user.roles.all()
        if not roles:
            return set()

        allowed_agent_ids = set()
        for role in roles:
            role_agents = await role.agents.all()
            allowed_agent_ids.update(agent.id for agent in role_agents)

        return allowed_agent_ids

    @staticmethod
    def build_search_filters(
        keyword: str | None = None,
        search_fields: list[str] | None = None,
        extra_filters: dict[str, Any] | None = None,
    ) -> Q:
        """Build search filter conditions"""
        filters = Q()

        # Keyword search
        if keyword and search_fields:
            keyword_filters = Q()
            for field in search_fields:
                keyword_filters |= Q(**{f"{field}__icontains": keyword})
            filters &= keyword_filters

        # Additional filter conditions
        if extra_filters:
            for field, value in extra_filters.items():
                if value is not None:
                    if field.endswith("__icontains"):
                        filters &= Q(**{field: value})
                    else:
                        filters &= Q(**{field: value})

        return filters


# Global instance
permission_service = PermissionService()
