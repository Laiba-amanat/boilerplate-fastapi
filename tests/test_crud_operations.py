"""CRUD operation tests"""

from httpx import AsyncClient


class TestCRUDOperations:
    """CRUD operation test class"""

    async def test_user_crud_full_cycle(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test complete user CRUD flow"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 1. Create user
        user_data = {
            "username": "crud_test_user",
            "email": "crud_test@test.com",
            "password": "Test123456",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        create_response = await async_client.post(
            "/api/v1/users/create", json=user_data, headers=headers
        )

        assert create_response.status_code == 200

        # 2. Get user list, verify user was created
        list_response = await async_client.get("/api/v1/users/list", headers=headers)

        assert list_response.status_code == 200
        users_data = list_response.json()["data"]

        # Find created user
        created_user = None
        for user in users_data:
            if user["username"] == "crud_test_user":
                created_user = user
                break

        assert created_user is not None
        assert created_user["email"] == "crud_test@test.com"
        assert created_user["is_active"] is True

        user_id = created_user["id"]

        # 3. Update user
        update_data = {
            "id": user_id,
            "username": "crud_test_updated",
            "email": "crud_test_updated@test.com",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        update_response = await async_client.post(
            "/api/v1/users/update", json=update_data, headers=headers
        )

        assert update_response.status_code == 200

        # 4. Verify update
        list_response_after_update = await async_client.get(
            "/api/v1/users/list", headers=headers
        )

        users_data_updated = list_response_after_update.json()["data"]
        updated_user = None
        for user in users_data_updated:
            if user["id"] == user_id:
                updated_user = user
                break

        assert updated_user is not None
        assert updated_user["username"] == "crud_test_updated"
        assert updated_user["email"] == "crud_test_updated@test.com"

        # 5. Delete user
        delete_response = await async_client.delete(
            f"/api/v1/users/delete?user_id={user_id}", headers=headers
        )

        assert delete_response.status_code == 200

        # 6. Verify deletion
        list_response_after_delete = await async_client.get(
            "/api/v1/users/list", headers=headers
        )

        users_data_final = list_response_after_delete.json()["data"]
        deleted_user = None
        for user in users_data_final:
            if user["id"] == user_id:
                deleted_user = user
                break

        # User should be deleted
        assert deleted_user is None

    async def test_user_creation_validation(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test user creation data validation"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Test invalid data
        invalid_cases = [
            # Missing username
            {
                "email": "test@test.com",
                "password": "Test123456",
                "is_active": True,
                "is_superuser": False,
                "role_ids": [],
            },
            # Missing email
            {
                "username": "test_user",
                "password": "Test123456",
                "is_active": True,
                "is_superuser": False,
                "role_ids": [],
            },
            # Missing password
            {
                "username": "test_user",
                "email": "test@test.com",
                "is_active": True,
                "is_superuser": False,
                "role_ids": [],
            },
            # Invalid email format
            {
                "username": "test_user",
                "email": "invalid_email",
                "password": "Test123456",
                "is_active": True,
                "is_superuser": False,
                "role_ids": [],
            },
        ]

        for invalid_data in invalid_cases:
            response = await async_client.post(
                "/api/v1/users/create", json=invalid_data, headers=headers
            )

            # Should return validation error
            assert response.status_code == 422

    async def test_duplicate_user_creation(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test creating duplicate user"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        user_data = {
            "username": "duplicate_test_user",
            "email": "duplicate_test@test.com",
            "password": "Test123456",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        # First creation should succeed
        first_response = await async_client.post(
            "/api/v1/users/create", json=user_data, headers=headers
        )

        assert first_response.status_code == 200

        # Second creation with same email should fail
        second_response = await async_client.post(
            "/api/v1/users/create", json=user_data, headers=headers
        )

        assert second_response.status_code == 400

    async def test_user_list_pagination(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test user list pagination"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Test pagination parameters
        response = await async_client.get(
            "/api/v1/users/list?page=1&page_size=5", headers=headers
        )

        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["page"] == 1
        assert data["page_size"] == 5

    async def test_user_search_functionality(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test user search functionality"""
        headers = {"Authorization": f"Bearer {admin_token}"}

        # First create a test user
        user_data = {
            "username": "search_test_user",
            "email": "search_test@test.com",
            "password": "Test123456",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        await async_client.post("/api/v1/users/create", json=user_data, headers=headers)

        # Test username search
        search_response = await async_client.get(
            "/api/v1/users/list?username=search_test", headers=headers
        )

        assert search_response.status_code == 200
        search_data = search_response.json()["data"]

        # Should find matching user
        found_user = False
        for user in search_data:
            if "search_test" in user["username"]:
                found_user = True
                break

        assert found_user

    async def test_nonexistent_user_operations(
        self, async_client: AsyncClient, admin_token: str
    ):
        """Test operations on non-existent user"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        nonexistent_id = 99999

        # Test updating non-existent user
        update_data = {
            "id": nonexistent_id,
            "username": "nonexistent_user",
            "email": "nonexistent@test.com",
            "is_active": True,
            "is_superuser": False,
            "role_ids": [],
        }

        update_response = await async_client.post(
            "/api/v1/users/update", json=update_data, headers=headers
        )

        # Should return error
        assert update_response.status_code in [400, 404]

        # Test deleting non-existent user
        delete_response = await async_client.delete(
            f"/api/v1/users/delete/{nonexistent_id}", headers=headers
        )

        # Should return error
        assert delete_response.status_code in [400, 404]
