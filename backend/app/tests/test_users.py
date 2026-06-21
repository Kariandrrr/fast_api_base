import pytest
from httpx import AsyncClient

DEFAULT_EMAIL = "owner@test.com"
DEFAULT_PASSWORD = "Test1234!"
DEFAULT_DISPLAY_NAME = "Test Owner"


class TestGetMe:
    async def test_success(self, auth_client: AsyncClient, registered_user: dict):
        r = await auth_client.get("/api/users/me")
        assert r.status_code == 200
        data = r.json()
        assert data["email"] == DEFAULT_EMAIL
        assert data["display_name"] == DEFAULT_DISPLAY_NAME
        assert "id" in data
        assert "password" not in data

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.get("/api/users/me")
        assert r.status_code == 401


class TestUpdateMe:
    async def test_update_display_name(self, auth_client: AsyncClient):
        r = await auth_client.patch("/api/users/me", json={"display_name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["display_name"] == "Updated Name"

    async def test_update_password(self, auth_client: AsyncClient):
        r = await auth_client.patch("/api/users/me", json={"password": "NewPass456!"})
        assert r.status_code == 200

    async def test_update_password_then_login_with_new(self, client: AsyncClient, auth_client: AsyncClient):
        new_password = "NewPass456!"
        r = await auth_client.patch("/api/users/me", json={"password": new_password})
        assert r.status_code == 200

        r = await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": new_password},
        )
        assert r.status_code == 204

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.patch("/api/users/me", json={"display_name": "New Name"})
        assert r.status_code == 401


class TestGetUserById:
    async def test_regular_user_gets_forbidden(self, auth_client: AsyncClient, registered_user: dict):
        r = await auth_client.get(f"/api/users/{registered_user['id']}")
        assert r.status_code == 403

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.get("/api/users/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 401


class TestDeleteMe:
    async def test_success(self, auth_client: AsyncClient):
        r = await auth_client.delete("/api/users/me")
        assert r.status_code == 204

    async def test_account_deactivated_after_delete(self, auth_client: AsyncClient):
        await auth_client.delete("/api/users/me")
        r = await auth_client.get("/api/users/me")
        assert r.status_code == 401

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.delete("/api/users/me")
        assert r.status_code == 401
