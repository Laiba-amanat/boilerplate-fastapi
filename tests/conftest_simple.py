"""Simplified test configuration to avoid complex dependencies"""

import asyncio
import os
import sys
from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings():
    """Test environment settings"""
    os.environ["DEBUG"] = "True"
    os.environ["APP_ENV"] = "testing"
    os.environ["DB_ENGINE"] = "sqlite"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only_32_chars_long"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Test Redis database


@pytest.fixture
def mock_app(test_settings):
    """Mock application to avoid Redis dependency"""
    from unittest.mock import Mock, patch

    # Mock Redis-related modules
    with patch("src.utils.cache.redis") as mock_redis:
        mock_redis.from_url.return_value = Mock()

        # Import and create application
        from src import app

        yield app


@pytest.fixture
def client(mock_app):
    """Synchronous test client"""
    with TestClient(mock_app) as c:
        yield c


@pytest.fixture
async def async_client(mock_app) -> AsyncGenerator[AsyncClient, None]:
    """Asynchronous test client"""
    async with AsyncClient(app=mock_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_jwt_token():
    """Sample JWT token"""
    from utils.jwt import create_token_pair

    access_token, refresh_token = create_token_pair(user_id=1)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "headers": {"Authorization": f"Bearer {access_token}"},
    }
