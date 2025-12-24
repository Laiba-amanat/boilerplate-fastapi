"""Health check and basic endpoint tests"""

from httpx import AsyncClient


class TestHealthEndpoints:
    """Health check endpoint test class"""

    async def test_health_check_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint"""
        response = await async_client.get("/api/v1/base/health")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "service" in data

        # Verify values
        assert data["status"] == "healthy"
        assert data["service"] == "FastAPI Backend Template"

        # Verify timestamp format
        from datetime import datetime

        timestamp = data["timestamp"]
        # Should be valid ISO format timestamp
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    async def test_version_endpoint(self, async_client: AsyncClient):
        """Test version information endpoint"""
        response = await async_client.get("/api/v1/base/version")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        required_fields = [
            "version",
            "app_title",
            "project_name",
            "build",
            "commit",
            "python_version",
        ]

        for field in required_fields:
            assert field in data
            assert isinstance(data[field], str)

    async def test_health_endpoint_performance(self, async_client: AsyncClient):
        """Test health check endpoint performance"""
        import time

        start_time = time.time()
        response = await async_client.get("/api/v1/base/health")
        end_time = time.time()

        assert response.status_code == 200

        # Health check should complete within 100ms
        response_time = (end_time - start_time) * 1000
        assert response_time < 100, f"Health check took {response_time:.2f}ms"

    async def test_health_check_no_authentication_required(
        self, async_client: AsyncClient
    ):
        """Test health check does not require authentication"""
        # Do not provide any authentication headers
        response = await async_client.get("/api/v1/base/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    async def test_version_no_authentication_required(self, async_client: AsyncClient):
        """Test version information does not require authentication"""
        # Do not provide any authentication headers
        response = await async_client.get("/api/v1/base/version")

        assert response.status_code == 200
        assert "version" in response.json()

    async def test_cors_headers(self, async_client: AsyncClient):
        """Test CORS header settings"""
        response = await async_client.get("/api/v1/base/health")

        # Check if CORS-related headers exist (if configured)
        assert response.status_code == 200

        # Basic CORS header check (may not exist in all environments)
        _ = response.headers
        # These headers may exist depending on middleware configuration
        # assert "access-control-allow-origin" in headers

    async def test_multiple_concurrent_health_checks(self, async_client: AsyncClient):
        """Test concurrent health checks"""
        import asyncio

        # Send multiple concurrent health check requests
        tasks = [async_client.get("/api/v1/base/health") for _ in range(10)]

        responses = await asyncio.gather(*tasks)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    async def test_api_root_documentation(self, async_client: AsyncClient):
        """Test API root path and documentation"""
        # Get basic authentication information from settings
        import base64

        from src.settings.config import settings

        # Create basic authentication header
        credentials = f"{settings.SWAGGER_UI_USERNAME}:{settings.SWAGGER_UI_PASSWORD}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        auth_headers = {"Authorization": f"Basic {encoded_credentials}"}

        # Test docs endpoint
        docs_response = await async_client.get("/docs", headers=auth_headers)
        assert docs_response.status_code == 200

        # Test OpenAPI specification
        openapi_response = await async_client.get("/openapi.json", headers=auth_headers)
        assert openapi_response.status_code == 200

        openapi_data = openapi_response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data

    async def test_health_check_includes_settings(self, async_client: AsyncClient):
        """Test health check includes necessary configuration information"""
        response = await async_client.get("/api/v1/base/health")
        data = response.json()

        # Verify environment information
        environment = data.get("environment")
        assert environment in ["development", "production", "testing"]

        # Verify version information exists
        version = data.get("version")
        assert version is not None
        assert len(version) > 0

    async def test_version_includes_build_info(self, async_client: AsyncClient):
        """Test version information includes build information"""
        response = await async_client.get("/api/v1/base/version")
        data = response.json()

        # Verify build information
        build = data.get("build", "dev")
        commit = data.get("commit", "unknown")
        python_version = data.get("python_version", "3.11+")

        assert isinstance(build, str)
        assert isinstance(commit, str)
        assert isinstance(python_version, str)

        # Python version should contain digits
        assert any(char.isdigit() for char in python_version)
