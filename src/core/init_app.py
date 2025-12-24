import asyncio
from functools import partial

from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from tortoise.expressions import Q

from api import api_router
from api.v1.base.base import limiter
from core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
    UnhandledExceptionHandle,
)
from core.middlewares import (
    BackGroundTaskMiddleware,
    HttpAuditLogMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from log import logger
from models.admin import Api, Menu, Role
from repositories.api import api_repository
from repositories.user import UserCreate, user_repository
from schemas.menus import MenuType
from settings.config import settings
from utils.cache import cache_manager


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS_LIST,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(SecurityHeadersMiddleware),  # Security headers middleware
        Middleware(RequestLoggingMiddleware),  # Request logging middleware
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/api/v1/base/access_token",
                "/docs",
                "/openapi.json",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)
    # Register general exception handler (must be placed last as fallback)
    app.add_exception_handler(Exception, UnhandledExceptionHandle)
    # Register rate limit exception handler
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def register_routers(app: FastAPI, prefix: str = "/api"):
    app.include_router(api_router, prefix=prefix)


async def init_superuser():
    logger.info("🔧 Starting superuser initialization...")
    user = await user_repository.model.exists()
    if not user:
        await user_repository.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password="abcd1234",
                is_active=True,
                is_superuser=True,
            )
        )
        logger.info("✅ Superuser created successfully - Username: admin")
    else:
        logger.info("ℹ️ Superuser already exists, skipping creation")


async def init_menus():
    logger.info("🔧 Starting system menu initialization...")
    menus = await Menu.exists()
    if not menus:
        parent_menu = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="System Management",
            path="/system",
            order=1,
            parent_id=0,
            icon="carbon:gui-management",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/system/user",
        )
        children_menu = [
            Menu(
                menu_type=MenuType.MENU,
                name="User Management",
                path="user",
                order=1,
                parent_id=parent_menu.id,
                icon="material-symbols:person-outline-rounded",
                is_hidden=False,
                component="/system/user",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="Role Management",
                path="role",
                order=2,
                parent_id=parent_menu.id,
                icon="carbon:user-role",
                is_hidden=False,
                component="/system/role",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="Menu Management",
                path="menu",
                order=3,
                parent_id=parent_menu.id,
                icon="material-symbols:list-alt-outline",
                is_hidden=False,
                component="/system/menu",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="API Management",
                path="api",
                order=4,
                parent_id=parent_menu.id,
                icon="ant-design:api-outlined",
                is_hidden=False,
                component="/system/api",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="Department Management",
                path="dept",
                order=5,
                parent_id=parent_menu.id,
                icon="mingcute:department-line",
                is_hidden=False,
                component="/system/dept",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="Audit Log",
                path="auditlog",
                order=6,
                parent_id=parent_menu.id,
                icon="ph:clipboard-text-bold",
                is_hidden=False,
                component="/system/auditlog",
                keepalive=False,
            ),
        ]
        await Menu.bulk_create(children_menu)
        await Menu.create(
            menu_type=MenuType.MENU,
            name="Top Level Menu",
            path="/top-menu",
            order=2,
            parent_id=0,
            icon="material-symbols:featured-play-list-outline",
            is_hidden=False,
            component="/top-menu",
            keepalive=False,
            redirect="",
        )
        logger.info("✅ System menu initialization successful - Menu count: 8")
    else:
        logger.info("ℹ️ System menus already exist, skipping initialization")


async def init_apis():
    logger.info("🔧 Starting API data initialization...")
    apis = await api_repository.model.exists()
    if not apis:
        await api_repository.refresh_api()
        api_count = await Api.all().count()
        logger.info(f"✅ API data initialization successful - API count: {api_count}")
    else:
        api_count = await Api.all().count()
        logger.info(f"ℹ️ API data already exists, skipping initialization - Current API count: {api_count}")


async def init_db():
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        await command.init_db(safe=True)
    except FileExistsError:
        pass

    await command.init()
    try:
        await command.migrate(no_input=True)
    except AttributeError as e:
        logger.error(f"Database migration failed: {e}")
        logger.warning("Please manually check database and migrations status")
        # No longer automatically delete migrations folder to avoid accidentally losing migration history
        # To reset migrations, manually execute: rm -rf migrations && uv run aerich init-db
        raise RuntimeError("Database migration failed, please check database connection and migrations status") from e

    await command.upgrade(run_in_transaction=True)


async def init_roles():
    logger.info("🔧 Starting user role initialization...")
    roles = await Role.exists()
    if not roles:
        admin_role = await Role.create(
            name="Administrator",
            desc="Administrator role",
        )
        user_role = await Role.create(
            name="Regular User",
            desc="Regular user role",
        )

        # Assign all APIs to administrator role
        all_apis = await Api.all()
        await admin_role.apis.add(*all_apis)
        # Assign all menus to administrator and regular user
        all_menus = await Menu.all()
        await admin_role.menus.add(*all_menus)
        await user_role.menus.add(*all_menus)

        # Assign basic APIs to regular user
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="Base Module"))
        await user_role.apis.add(*basic_apis)

        logger.info("✅ User role initialization successful - Roles: Administrator, Regular User")
    else:
        role_count = await Role.all().count()
        logger.info(f"ℹ️ User roles already exist, skipping initialization - Current role count: {role_count}")


async def init_data():
    logger.info("🚀 System initialization starting...")

    logger.info("🔧 Starting database initialization and migration...")
    await init_db()
    logger.info("✅ Database initialization completed")

    logger.info("🔄 Initializing base data in parallel...")
    await asyncio.gather(
        init_superuser(),
        init_menus(),
        init_apis(),
    )
    logger.info("✅ Base data initialization completed")

    await init_roles()

    logger.info("🎉 System initialization completed!")


async def startup():
    """Application startup event"""
    logger.info("🚀 FastAPI application starting...")

    # Initialize Redis connection
    await cache_manager.connect()

    # Initialize database
    await init_data()


async def shutdown():
    """Application shutdown event"""
    logger.info("🛑 FastAPI application shutting down...")

    # Disconnect Redis connection
    await cache_manager.disconnect()


async def init_app(app: FastAPI):
    """Initialize on application startup"""
    # Register startup and shutdown events
    app.add_event_handler("startup", startup)
    app.add_event_handler("shutdown", shutdown)
    logger.info("🎉 FastAPI application startup completed!")


async def stop_app(app: FastAPI):
    """Cleanup on application shutdown"""
    logger.info("🔧 Starting system service shutdown...")
    logger.info("👋 System service has been shut down")


def register_startup_event(app: FastAPI):
    """Register startup and shutdown events"""
    app.add_event_handler("startup", partial(init_app, app))
    app.add_event_handler("shutdown", partial(stop_app, app))
