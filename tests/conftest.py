"""Test configuration and fixtures"""

import asyncio
import os
import subprocess
import sys
import tempfile
import warnings
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("SWAGGER_UI_PASSWORD", "test_password")
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("APP_TITLE", "FastAPI Backend Template")
os.environ.setdefault("PROJECT_NAME", "FastAPI Backend Template")

try:  # pragma: no cover - fallback for environments without pytest-asyncio
    import pytest_asyncio  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pip", "install", "pytest-asyncio>=0.23,<0.24"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        warnings.warn(
            "Installed pytest-asyncio dynamically to enable async fixtures."
        )
        import pytest_asyncio  # type: ignore  # noqa: F401
    except Exception as exc:  # pragma: no cover
        warnings.warn(
            f"pytest-asyncio is required for async tests but could not be installed: {exc}"
        )

if "pytest_asyncio" in sys.modules:  # pragma: no cover - plugin auto-registration helper
    pytest_plugins = ("pytest_asyncio",)

from src import app
from tortoise import Tortoise


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop"""
    # Set test environment variables
    import os

    os.environ["TESTING"] = "true"

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Set up test database"""
    # Use temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()

    db_url = f"sqlite://{temp_db.name}"

    # Initialize Tortoise ORM
    test_config = {
        "connections": {"default": db_url},
        "apps": {
            "models": {
                "models": ["models", "aerich.models"],
                "default_connection": "default",
            }
        },
        "use_tz": False,
        "timezone": "Asia/Shanghai",
    }

    await Tortoise.init(config=test_config)

    # Generate database schema
    await Tortoise.generate_schemas()

    yield

    # Cleanup
    await Tortoise.close_connections()
    os.unlink(temp_db.name)


@pytest.fixture
def client():
    """Synchronous test client"""
    with TestClient(app) as c:
        yield c


@pytest.fixture
async def clean_database():
    """Clean database"""
    from src.models.admin import Api, AuditLog, Dept, FileMapping, Menu, Role, User

    try:
        # Clean all test data (ignore foreign key constraint errors)
        await User.all().delete()
        await Role.all().delete()
        await Api.all().delete()
        await Menu.all().delete()
        await Dept.all().delete()
        await AuditLog.all().delete()
        await FileMapping.all().delete()
    except Exception:
        # If deletion fails, database may not be initialized, skip directly
        pass


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous test client"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_token(async_client: AsyncClient, clean_database) -> str:
    """Get admin token"""
    import os
    import uuid

    from src.repositories.user import user_repository
    from src.schemas.users import UserCreate

    # Ensure test environment variables are set
    os.environ["TESTING"] = "true"

    # Use random username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    admin_user = UserCreate(
        username=f"admin_{unique_id}",
        email=f"admin_{unique_id}@test.com",
        password="Test123456",
        is_superuser=True,
        is_active=True,
    )

    try:
        await user_repository.create_user(obj_in=admin_user)
    except Exception as e:
        print(f"Failed to create user: {e}")
        raise

    # Login to get token, with retry mechanism
    import time

    for attempt in range(5):  # Increase retry count
        try:
            response = await async_client.post(
                "/api/v1/base/access_token",
                json={"username": f"admin_{unique_id}", "password": "Test123456"},
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("data", {}).get("access_token")
                if token:
                    return token
                else:
                    print(f"No token in response data: {data}")
                    raise Exception("Token not found in response")
            elif response.status_code == 429:  # Rate limit
                print(f"Encountered rate limit, waiting before retry (attempt {attempt + 1}/5)")
                time.sleep(2)
                continue
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
                if attempt < 4:  # Not the last attempt
                    time.sleep(1)
                    continue
                raise Exception(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Login attempt {attempt + 1} failed: {e}")
            if attempt == 4:  # Last attempt
                raise e
            time.sleep(1)

    raise Exception("All login attempts failed")


@pytest.fixture
async def normal_user_token(async_client: AsyncClient, clean_database) -> str:
    """Get normal user token"""
    import os
    import uuid

    from src.repositories.user import user_repository
    from src.schemas.users import UserCreate

    # Ensure test environment variables are set
    os.environ["TESTING"] = "true"

    # Use random username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    normal_user = UserCreate(
        username=f"user_{unique_id}",
        email=f"user_{unique_id}@test.com",
        password="Test123456",
        is_superuser=False,
        is_active=True,
    )

    try:
        await user_repository.create_user(obj_in=normal_user)
    except Exception as e:
        print(f"Failed to create normal user: {e}")
        raise

    # Login to get token, with retry mechanism
    import time

    for attempt in range(5):
        try:
            response = await async_client.post(
                "/api/v1/base/access_token",
                json={"username": f"user_{unique_id}", "password": "Test123456"},
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("data", {}).get("access_token")
                if token:
                    return token
                else:
                    print(f"No token in normal user response data: {data}")
                    raise Exception("Token not found in response")
            elif response.status_code == 429:  # Rate limit
                print(f"Normal user encountered rate limit, waiting before retry (attempt {attempt + 1}/5)")
                time.sleep(2)
                continue
            else:
                print(f"Normal user login failed: {response.status_code} - {response.text}")
                if attempt < 4:  # Not the last attempt
                    time.sleep(1)
                    continue
                raise Exception(
                    f"Normal user login failed: {response.status_code} - {response.text}"
                )
        except Exception as e:
            print(f"Normal user login attempt {attempt + 1} failed: {e}")
            if attempt == 4:  # Last attempt
                raise e
            time.sleep(1)

    raise Exception("All normal user login attempts failed")


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Authentication headers"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def normal_auth_headers(normal_user_token: str) -> dict:
    """Normal user authentication headers"""
    return {"Authorization": f"Bearer {normal_user_token}"}
