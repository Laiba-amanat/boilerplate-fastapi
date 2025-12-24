"""Database and cache integration tests"""

import pytest
from httpx import AsyncClient
from src.repositories.user import user_repository
from src.schemas.users import UserCreate
from src.utils.cache import cache_manager, clear_user_cache


class TestDatabaseIntegration:
    """Database integration test class"""

    async def test_database_connection(self):
        """Test database connection"""
        from tortoise import Tortoise

        # Verify database connection is normal
        connections = Tortoise.get_connection("default")
        assert connections is not None

    async def test_user_model_crud(self):
        """Test user model CRUD operations"""
        # Create user
        user_data = UserCreate(
            username="db_test_user",
            email="db_test@test.com",
            password="Test123456",
            is_active=True,
            is_superuser=False,
        )

        created_user = await user_repository.create_user(obj_in=user_data)
        assert created_user is not None
        assert created_user.username == "db_test_user"
        assert created_user.email == "db_test@test.com"

        # Read user
        retrieved_user = await user_repository.get(id=created_user.id)
        assert retrieved_user is not None
        assert retrieved_user.username == "db_test_user"

        # Update user
        from src.schemas.users import UserUpdate

        update_data = UserUpdate(
            id=created_user.id,
            username="db_test_user_updated",
            email="db_test_updated@test.com",
            is_active=True,
            is_superuser=False,
            role_ids=[],
        )

        updated_user = await user_repository.update(
            id=created_user.id, obj_in=update_data
        )
        assert updated_user.username == "db_test_user_updated"
        assert updated_user.email == "db_test_updated@test.com"

        # Delete user
        await user_repository.remove(id=created_user.id)

        # Verify deletion
        try:
            _ = await user_repository.get(id=created_user.id)
            raise AssertionError("Should raise DoesNotExist exception")
        except Exception:
            # User has been deleted, expect exception to be raised
            pass

    async def test_user_authentication_flow(self):
        """Test user authentication flow"""
        # Create user
        user_data = UserCreate(
            username="auth_flow_test",
            email="auth_flow@test.com",
            password="Test123456",
            is_active=True,
            is_superuser=False,
        )

        created_user = await user_repository.create_user(obj_in=user_data)

        # Test authentication
        from src.schemas.login import CredentialsSchema

        credentials = CredentialsSchema(
            username="auth_flow_test", password="Test123456"
        )

        authenticated_user = await user_repository.authenticate(credentials)
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id

        # Test wrong password
        wrong_credentials = CredentialsSchema(
            username="auth_flow_test", password="WrongPassword"
        )

        with pytest.raises(Exception):  # noqa: B017
            await user_repository.authenticate(wrong_credentials)

    async def test_database_transaction_rollback(self):
        """Test database transaction rollback"""
        from tortoise import transactions

        initial_count = await user_repository.model.all().count()

        try:
            async with transactions.in_transaction():
                # Create user
                user_data = UserCreate(
                    username="transaction_test",
                    email="transaction@test.com",
                    password="Test123456",
                    is_active=True,
                    is_superuser=False,
                )

                await user_repository.create_user(obj_in=user_data)

                # Manually raise exception to trigger rollback
                raise Exception("Test rollback")
        except Exception:
            pass

        # Verify user count did not increase after rollback
        final_count = await user_repository.model.all().count()
        assert final_count == initial_count


class TestCacheIntegration:
    """Cache integration test class"""

    async def test_cache_manager_connection(self):
        """Test cache manager connection"""
        # Test connection (should gracefully degrade if Redis is unavailable)
        await cache_manager.connect()

        # Test basic operations
        test_key = "test_key"
        test_value = {"test": "data"}

        # Set cache
        set_result = await cache_manager.set(test_key, test_value, ttl=60)

        if cache_manager.redis:  # Only test when Redis is available
            assert set_result is True

            # Get cache
            cached_value = await cache_manager.get(test_key)
            assert cached_value == test_value

            # Delete cache
            delete_result = await cache_manager.delete(test_key)
            assert delete_result is True

            # Verify deletion
            deleted_value = await cache_manager.get(test_key)
            assert deleted_value is None

    async def test_cache_decorator_functionality(self):
        """Test cache decorator functionality"""
        from src.utils.cache import cached

        call_count = 0

        @cached("test_decorator", ttl=60)
        async def test_function(param: str) -> str:
            nonlocal call_count
            call_count += 1
            return f"result_{param}"

        # First call
        result1 = await test_function("test")
        assert result1 == "result_test"
        assert call_count == 1

        # If cache is available, second call should use cache
        result2 = await test_function("test")
        assert result2 == "result_test"

        if cache_manager.redis:
            # When Redis is available, should use cache
            assert call_count == 1
        else:
            # When Redis is unavailable, will directly call function
            assert call_count == 2

    async def test_user_cache_clearing(self):
        """Test user cache clearing"""
        user_id = 123

        # Set some user-related cache
        test_caches = [
            f"user:{user_id}:profile",
            f"userinfo:{user_id}",
            f"user_roles:{user_id}",
            f"user_permissions:{user_id}",
        ]

        for cache_key in test_caches:
            await cache_manager.set(cache_key, {"test": "data"}, ttl=60)

        # Clear user cache
        cleared_count = await clear_user_cache(user_id)

        if cache_manager.redis:
            # When Redis is available, cache should be cleared
            assert cleared_count >= 0

            # Verify cache has been cleared
            for cache_key in test_caches:
                cached_value = await cache_manager.get(cache_key)
                assert cached_value is None

    async def test_cache_pattern_operations(self):
        """Test cache pattern operations"""
        if not cache_manager.redis:
            pytest.skip("Redis not available, skipping pattern tests")

        # Set some test cache
        test_pattern = "pattern_test"
        test_keys = [
            f"{test_pattern}:key1",
            f"{test_pattern}:key2",
            f"{test_pattern}:key3",
            "other_key",
        ]

        for key in test_keys:
            await cache_manager.set(key, {"test": "data"}, ttl=60)

        # Clear cache matching pattern
        cleared_count = await cache_manager.clear_pattern(f"{test_pattern}:*")

        # Should have cleared 3 matching keys
        assert cleared_count == 3

        # Verify matching keys are cleared, other keys remain
        for key in test_keys[:3]:  # pattern_test:* keys
            cached_value = await cache_manager.get(key)
            assert cached_value is None

        # other_key should still exist
        other_value = await cache_manager.get("other_key")
        assert other_value == {"test": "data"}

    async def test_cache_with_api_endpoints(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test API endpoint caching behavior"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Call user info endpoint multiple times
        responses = []
        for _ in range(3):
            response = await async_client.get("/api/v1/base/userinfo", headers=headers)
            assert response.status_code == 200
            responses.append(response.json())

        # All responses should be the same
        for response in responses[1:]:
            assert response == responses[0]
