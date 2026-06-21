import pytest
from httpx import AsyncClient

DEFAULT_EMAIL = "owner@test.com"
DEFAULT_PASSWORD = "Test1234!"
DEFAULT_DISPLAY_NAME = "Test Owner"


class TestCookieRegister:
    async def test_success(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/register",
            json={"email": "new@test.com", "password": DEFAULT_PASSWORD, "display_name": "New User"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "new@test.com"
        assert data["display_name"] == "New User"
        assert "id" in data
        assert "password" not in data

    async def test_duplicate_email(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/cookie/register",
            json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD, "display_name": "Dup"},
        )
        assert r.status_code == 400

    async def test_invalid_email(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/register",
            json={"email": "not-an-email", "password": DEFAULT_PASSWORD, "display_name": "Bad"},
        )
        assert r.status_code == 422

    async def test_missing_display_name(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/register",
            json={"email": "test@test.com", "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 422


class TestCookieLogin:
    async def test_success(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 204

    async def test_wrong_password(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": "WrongPass123!"},
        )
        assert r.status_code == 400

    async def test_wrong_email(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/login",
            data={"username": "nobody@test.com", "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 400


class TestCookieLogout:
    async def test_success(self, auth_client: AsyncClient):
        r = await auth_client.post("/api/auth/cookie/logout")
        assert r.status_code == 204

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.post("/api/auth/cookie/logout")
        assert r.status_code == 401

    async def test_access_rejected_after_logout(self, auth_client: AsyncClient):
        await auth_client.post("/api/auth/cookie/logout")
        r = await auth_client.get("/api/users/me")
        assert r.status_code == 401

    async def test_refresh_rejected_after_logout(self, auth_client: AsyncClient):
        await auth_client.post("/api/auth/cookie/logout")
        r = await auth_client.post("/api/auth/cookie/refresh")
        assert r.status_code == 401


class TestCookieLogoutAll:
    async def test_success(self, auth_client: AsyncClient):
        r = await auth_client.post("/api/auth/cookie/logout-all")
        assert r.status_code == 204

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.post("/api/auth/cookie/logout-all")
        assert r.status_code == 401

    async def test_access_rejected_after_logout_all(self, auth_client: AsyncClient):
        await auth_client.post("/api/auth/cookie/logout-all")
        r = await auth_client.get("/api/users/me")
        assert r.status_code == 401

    async def test_second_session_rejected_after_logout_all(self, client: AsyncClient, registered_user: dict):
        from httpx import AsyncClient as _Client, ASGITransport
        from app.app import main_app

        await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        async with _Client(transport=ASGITransport(app=main_app), base_url="http://test") as client2:
            await client2.post(
                "/api/auth/cookie/login",
                data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
            )
            r_before = await client2.get("/api/users/me")
            assert r_before.status_code == 200

            await client.post("/api/auth/cookie/logout-all")

            r_after = await client2.get("/api/users/me")
            assert r_after.status_code == 401


class TestCookieRefresh:
    async def test_success(self, auth_client: AsyncClient):
        r = await auth_client.post("/api/auth/cookie/refresh")
        assert r.status_code == 204

    async def test_no_cookies(self, client: AsyncClient):
        r = await client.post("/api/auth/cookie/refresh")
        assert r.status_code == 401


class TestCookieRequestVerifyToken:
    async def test_existing_user(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/cookie/request-verify-token",
            json={"email": DEFAULT_EMAIL},
        )
        assert r.status_code == 202

    async def test_nonexistent_user_does_not_leak(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/request-verify-token",
            json={"email": "nobody@test.com"},
        )
        assert r.status_code == 202


class TestCookieVerify:
    async def test_invalid_token(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/verify",
            json={"token": "invalid.token.value"},
        )
        assert r.status_code == 400


class TestCookieForgotPassword:
    async def test_existing_user(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/cookie/forgot-password",
            json={"email": DEFAULT_EMAIL},
        )
        assert r.status_code == 202

    async def test_nonexistent_user_does_not_leak(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/forgot-password",
            json={"email": "nobody@test.com"},
        )
        assert r.status_code == 202


class TestCookieResetPassword:
    async def test_invalid_token(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/cookie/reset-password",
            json={"token": "invalid.token.value", "password": "NewPass123!"},
        )
        assert r.status_code == 400
