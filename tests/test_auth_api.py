"""Authentication API tests"""

from httpx import AsyncClient


class TestAuthAPI:
    """Authentication API test class"""

    async def test_login_success(self, async_client: AsyncClient):
        """Test successful login"""
        # First create user
        from src.repositories.user import user_repository
        from src.schemas.users import UserCreate

        user_data = UserCreate(
            username="login_test_user",
            email="login_test@test.com",
            password="Test123456",
            is_active=True,
            is_superuser=False,
        )

        await user_repository.create_user(obj_in=user_data)

        # Test login
        response = await async_client.post(
            "/api/v1/base/access_token",
            json={"username": "login_test_user", "password": "Test123456"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]
        assert "username" in data["data"]
        assert "expires_in" in data["data"]
        assert data["data"]["username"] == "login_test_user"
        assert data["data"]["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        response = await async_client.post(
            "/api/v1/base/access_token",
            json={"username": "nonexistent_user", "password": "wrong_password"},
        )

        assert response.status_code == 400 or response.status_code == 401

    async def test_login_inactive_user(self, async_client: AsyncClient):
        """Test login with inactive user"""
        from src.repositories.user import user_repository
        from src.schemas.users import UserCreate

        # Create inactive user
        user_data = UserCreate(
            username="inactive_user",
            email="inactive@test.com",
            password="Test123456",
            is_active=False,  # Inactive status
            is_superuser=False,
        )

        await user_repository.create_user(obj_in=user_data)

        # Attempt login
        response = await async_client.post(
            "/api/v1/base/access_token",
            json={"username": "inactive_user", "password": "Test123456"},
        )

        assert response.status_code == 400 or response.status_code == 401

    async def test_refresh_token_success(self, async_client: AsyncClient):
        """Test successful token refresh"""
        # First login to get token
        from src.repositories.user import user_repository
        from src.schemas.users import UserCreate

        user_data = UserCreate(
            username="refresh_test_user",
            email="refresh_test@test.com",
            password="Test123456",
            is_active=True,
            is_superuser=False,
        )

        await user_repository.create_user(obj_in=user_data)

        # Login
        login_response = await async_client.post(
            "/api/v1/base/access_token",
            json={"username": "refresh_test_user", "password": "Test123456"},
        )

        login_data = login_response.json()["data"]
        refresh_token = login_data["refresh_token"]

        # Wait 1 second to ensure different timestamps
        import asyncio

        await asyncio.sleep(1)

        # Use refresh token to get new token pair
        refresh_response = await async_client.post(
            "/api/v1/base/refresh_token", json={"refresh_token": refresh_token}
        )

        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()["data"]

        assert "access_token" in refresh_data
        assert "refresh_token" in refresh_data
        assert "expires_in" in refresh_data
        assert refresh_data["token_type"] == "bearer"

        # New tokens should be different from original tokens
        assert refresh_data["access_token"] != login_data["access_token"]
        assert refresh_data["refresh_token"] != login_data["refresh_token"]

    async def test_refresh_token_invalid(self, async_client: AsyncClient):
        """Test invalid refresh token"""
        response = await async_client.post(
            "/api/v1/base/refresh_token",
            json={"refresh_token": "invalid.refresh.token"},
        )

        assert response.status_code == 401

    async def test_refresh_token_access_token_used(self, async_client: AsyncClient):
        """Test using access token for refresh operation"""
        # First login to get token
        from src.repositories.user import user_repository
        from src.schemas.users import UserCreate

        user_data = UserCreate(
            username="token_type_test_user",
            email="token_type_test@test.com",
            password="Test123456",
            is_active=True,
            is_superuser=False,
        )

        await user_repository.create_user(obj_in=user_data)

        # Login
        login_response = await async_client.post(
            "/api/v1/base/access_token",
            json={"username": "token_type_test_user", "password": "Test123456"},
        )

        login_data = login_response.json()["data"]
        access_token = login_data["access_token"]

        # Attempt to use access token for refresh (should fail)
        refresh_response = await async_client.post(
            "/api/v1/base/refresh_token", json={"refresh_token": access_token}
        )

        assert refresh_response.status_code == 401

    async def test_get_userinfo_with_valid_token(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test getting user info with valid token"""
        response = await async_client.get(
            "/api/v1/base/userinfo", headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        assert "username" in data
        assert "email" in data
        assert "is_superuser" in data
        assert "is_active" in data

    async def test_get_userinfo_without_token(self, async_client: AsyncClient):
        """Test getting user info without token"""
        response = await async_client.get("/api/v1/base/userinfo")

        assert response.status_code == 401

    async def test_get_userinfo_with_invalid_token(self, async_client: AsyncClient):
        """Test getting user info with invalid token"""
        response = await async_client.get(
            "/api/v1/base/userinfo",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401
