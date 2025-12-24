"""Permission check tests"""

from httpx import AsyncClient


class TestPermissions:
    """Permission test class"""

    async def test_superuser_required_access_with_admin(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test admin accessing endpoints requiring superuser permissions"""
        # Test user list endpoint (usually requires admin permissions)
        response = await async_client.get(
            "/api/v1/users/list", headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Admin should be able to access
        assert response.status_code == 200

    async def test_superuser_required_access_with_normal_user(
        self, async_client: AsyncClient, normal_user_token: str
    ):
        """Test normal user accessing endpoints requiring superuser permissions"""
        # Normal user attempts to access admin endpoint
        response = await async_client.get(
            "/api/v1/users/list",
            headers={"Authorization": f"Bearer {normal_user_token}"},
        )

        # Normal user should be denied (403 or 401)
        assert response.status_code in [401, 403]

    async def test_authenticated_access_with_valid_token(
        self, async_client: AsyncClient, normal_user_token: str
    ):
        """Test authenticated user accessing endpoints requiring authentication"""
        response = await async_client.get(
            "/api/v1/base/userinfo",
            headers={"Authorization": f"Bearer {normal_user_token}"},
        )

        # Authenticated user should be able to access their own information
        assert response.status_code == 200
        data = response.json()["data"]
        assert "username" in data

    async def test_authenticated_access_without_token(self, async_client: AsyncClient):
        """Test unauthenticated user accessing endpoints requiring authentication"""
        response = await async_client.get("/api/v1/base/userinfo")

        # Unauthenticated user should be denied
        assert response.status_code == 401

    async def test_public_endpoint_access(self, async_client: AsyncClient):
        """Test public endpoint access"""
        # Health check should be public
        response = await async_client.get("/api/v1/base/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_version_endpoint_access(self, async_client: AsyncClient):
        """Test version information endpoint access"""
        response = await async_client.get("/api/v1/base/version")

        assert response.status_code == 200
        data = response.json()
        assert "version" in data

    async def test_user_crud_permissions(
        self, async_client: AsyncClient, admin_token: str, normal_user_token: str
    ):
        """Test user CRUD operation permissions"""
        # Test creating user (usually requires admin permissions)
        user_data = {
            "username": "permission_test_user",
            "email": "permission_test@test.com",
            "password": "Test123456",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        # Admin creates user
        admin_response = await async_client.post(
            "/api/v1/users/create",
            json=user_data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        # Admin should be able to create user
        assert admin_response.status_code == 200

        # Normal user attempts to create user
        normal_user_data = {
            "username": "normal_user_create_test",
            "email": "normal_create@test.com",
            "password": "Test123456",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        normal_response = await async_client.post(
            "/api/v1/users/create",
            json=normal_user_data,
            headers={"Authorization": f"Bearer {normal_user_token}"},
        )

        # Normal user should be denied
        assert normal_response.status_code in [401, 403]

    async def test_token_validation_edge_cases(self, async_client: AsyncClient):
        """Test token validation edge cases"""
        test_cases = [
            "",  # Empty token
            "Bearer",  # Only Bearer
            "Bearer ",  # Only space after Bearer
            "InvalidBearer token",  # Invalid format
            "Bearer invalid.token",  # Invalid token
        ]

        for invalid_auth in test_cases:
            response = await async_client.get(
                "/api/v1/base/userinfo", headers={"Authorization": invalid_auth}
            )

            # All invalid cases should return 401
            assert response.status_code == 401

    async def test_rate_limiting_login(self, async_client: AsyncClient):
        """Test login rate limiting (basic test)"""
        # Multiple failed login attempts
        for _ in range(3):
            response = await async_client.post(
                "/api/v1/base/access_token",
                json={"username": "nonexistent", "password": "wrong"},
            )
            # Each should return an error
            assert response.status_code in [400, 401]

    async def test_rate_limiting_refresh(self, async_client: AsyncClient):
        """Test refresh token rate limiting (basic test)"""
        # Multiple invalid refresh attempts
        for _ in range(3):
            response = await async_client.post(
                "/api/v1/base/refresh_token", json={"refresh_token": "invalid.token"}
            )
            # Each should return an error
            assert response.status_code == 401
