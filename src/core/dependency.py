import re
import secrets
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

from core.ctx import CTX_USER_ID
from models import Role, User
from settings.config import settings

security = HTTPBasic()
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_UI_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_UI_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Required",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class AuthControl:
    @classmethod
    async def is_authed(
        cls, token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
    ) -> Optional["User"]:
        try:
            # Directly use token provided by HTTPBearer (Bearer prefix already removed)
            if token is None or not token.credentials:
                raise HTTPException(
                    status_code=401, detail="Missing authentication token"
                )

            decode_data = jwt.decode(
                token.credentials,
                settings.SECRET_KEY,
                algorithms=settings.JWT_ALGORITHM,
            )
            user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail="Login has expired") from e
        except Exception as e:
            # Log detailed error information but don't return it to user
            raise HTTPException(status_code=401, detail="Authentication failed") from e


class PermissionControl:
    @classmethod
    async def has_permission(
        cls,
        request: Request,
        current_user: User = Depends(AuthControl.is_authed),
    ) -> None:
        """Check if user has permission to access specified API

        Args:
            request: FastAPI request object
            current_user: Current authenticated user

        Raises:
            HTTPException: Raises 403 error when user has no permission
        """
        if current_user.is_superuser:
            return

        method = request.method
        path = request.url.path
        roles: list[Role] = await current_user.roles.all()

        if not roles:
            raise HTTPException(
                status_code=403, detail="The user is not bound to a role"
            )

        # Get API permissions for all user roles
        apis = [await role.apis.all() for role in roles]
        permission_apis = [(api.method, api.path) for api in sum(apis, [])]

        # Check permission match (supports path parameters)
        for perm_method, perm_path in permission_apis:
            if method == perm_method:
                # Convert path parameter placeholders to regular expressions
                # Example: /api/v1/agent/{agent_id} -> /api/v1/agent/[^/]+
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", perm_path)
                pattern = f"^{pattern}$"
                if re.match(pattern, path):
                    return

        raise HTTPException(
            status_code=403,
            detail=f"Permission denied method:{method} path:{path}",
        )


class AgentPermissionControl:
    """Agent permission control class"""

    @classmethod
    async def has_agent_permission(
        cls,
        request: Request,
        current_user: User = Depends(AuthControl.is_authed),
    ) -> User:
        """Check if user has permission to access agent

        Args:
            request: FastAPI request object
            current_user: Current authenticated user

        Returns:
            User: Current user object

        Raises:
            HTTPException: Raises 403 error when user has no permission
        """
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user

        # Extract agent_id from URL path
        path_params = request.path_params
        agent_id = path_params.get("agent_id")

        if not agent_id:
            raise HTTPException(status_code=400, detail="Missing agent ID parameter")

        try:
            agent_id = int(agent_id)
        except (ValueError, TypeError) as e:
            raise HTTPException(status_code=400, detail="Invalid agent ID") from e

        # Get user roles
        roles: list[Role] = await current_user.roles.all()
        if not roles:
            raise HTTPException(
                status_code=403, detail="User is not bound to a role, no permission to access agent"
            )

        # Check if user roles have permission to access this agent
        for role in roles:
            role_agents = await role.agents.all()
            if any(agent.id == agent_id for agent in role_agents):
                return current_user

        raise HTTPException(status_code=403, detail="No permission to access this agent")

    @classmethod
    async def filter_agents_by_permission(
        cls,
        current_user: User = Depends(AuthControl.is_authed),
    ) -> set[int]:
        """Get set of agent IDs user has permission to access

        Args:
            current_user: Current authenticated user

        Returns:
            set[int]: Set of agent IDs user has permission to access, superuser returns empty set indicating no restrictions
        """
        # Superuser has all permissions, return empty set indicating no restrictions
        if current_user.is_superuser:
            return set()

        # Get all agent IDs associated with user roles
        roles: list[Role] = await current_user.roles.all()
        if not roles:
            return set()  # No roles, return empty set

        allowed_agent_ids = set()
        for role in roles:
            role_agents = await role.agents.all()
            allowed_agent_ids.update(agent.id for agent in role_agents)

        return allowed_agent_ids


DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
DependAgentPermission = Depends(AgentPermissionControl.has_agent_permission)
DependAgentFilter = Depends(AgentPermissionControl.filter_agents_by_permission)
