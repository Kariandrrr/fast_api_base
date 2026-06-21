import pytest
from httpx import AsyncClient

DEFAULT_EMAIL = "owner@test.com"
DEFAULT_PASSWORD = "Test1234!"
DEFAULT_DISPLAY_NAME = "Test Owner"


@pytest.fixture
async def bearer_tokens(client: AsyncClient, registered_user: dict) -> dict:
    r = await client.post(
        "/api/auth/bearer/login",
        data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
    )
    assert r.status_code == 200
    return r.json()


class TestBearerRegister:
    async def test_success(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/register",
            json={"email": "bearer@test.com", "password": DEFAULT_PASSWORD, "display_name": "Bearer User"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "bearer@test.com"
        assert "id" in data
        assert "password" not in data

    async def test_duplicate_email(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/register",
            json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD, "display_name": "Dup"},
        )
        assert r.status_code == 400

    async def test_invalid_email(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/register",
            json={"email": "bad-email", "password": DEFAULT_PASSWORD, "display_name": "Bad"},
        )
        assert r.status_code == 422

    async def test_missing_display_name(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/register",
            json={"email": "test@test.com", "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 422


class TestBearerLogin:
    async def test_success(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_wrong_password(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": "WrongPass123!"},
        )
        assert r.status_code == 400

    async def test_wrong_email(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/login",
            data={"username": "nobody@test.com", "password": DEFAULT_PASSWORD},
        )
        assert r.status_code == 400


class TestBearerLogout:
    async def test_success(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        r = await client.post(
            "/api/auth/bearer/logout",
            json={"refresh_token": bearer_tokens["refresh_token"]},
            headers=headers,
        )
        assert r.status_code == 204

    async def test_unauthenticated(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/logout",
            json={"refresh_token": "some-token"},
        )
        assert r.status_code == 401

    async def test_access_token_rejected_after_logout(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        await client.post(
            "/api/auth/bearer/logout",
            json={"refresh_token": bearer_tokens["refresh_token"]},
            headers=headers,
        )
        r = await client.get("/api/users/me", headers=headers)
        assert r.status_code == 401

    async def test_refresh_token_rejected_after_logout(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        await client.post(
            "/api/auth/bearer/logout",
            json={"refresh_token": bearer_tokens["refresh_token"]},
            headers=headers,
        )
        r = await client.post(
            "/api/auth/bearer/refresh",
            json={
                "access_token": bearer_tokens["access_token"],
                "refresh_token": bearer_tokens["refresh_token"],
            },
        )
        assert r.status_code == 401


class TestBearerLogoutAll:
    async def test_success(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        r = await client.post("/api/auth/bearer/logout-all", headers=headers)
        assert r.status_code == 204

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.post("/api/auth/bearer/logout-all")
        assert r.status_code == 401

    async def test_access_token_rejected_after_logout_all(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        await client.post("/api/auth/bearer/logout-all", headers=headers)
        r = await client.get("/api/users/me", headers=headers)
        assert r.status_code == 401

    async def test_second_session_rejected_after_logout_all(self, client: AsyncClient, registered_user: dict):
        r1 = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        tokens1 = r1.json()
        r2 = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        tokens2 = r2.json()

        headers1 = {"Authorization": f"Bearer {tokens1['access_token']}"}
        await client.post("/api/auth/bearer/logout-all", headers=headers1)

        headers2 = {"Authorization": f"Bearer {tokens2['access_token']}"}
        r = await client.get("/api/users/me", headers=headers2)
        assert r.status_code == 401


class TestBearerRefresh:
    async def test_success(self, client: AsyncClient, bearer_tokens: dict):
        r = await client.post(
            "/api/auth/bearer/refresh",
            json={
                "access_token": bearer_tokens["access_token"],
                "refresh_token": bearer_tokens["refresh_token"],
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_invalid_refresh_token(self, client: AsyncClient, bearer_tokens: dict):
        r = await client.post(
            "/api/auth/bearer/refresh",
            json={
                "access_token": bearer_tokens["access_token"],
                "refresh_token": "invalid.token.value",
            },
        )
        assert r.status_code == 401

    async def test_tokens_rotate_on_refresh(self, client: AsyncClient, bearer_tokens: dict):
        r = await client.post(
            "/api/auth/bearer/refresh",
            json={
                "access_token": bearer_tokens["access_token"],
                "refresh_token": bearer_tokens["refresh_token"],
            },
        )
        assert r.status_code == 200
        new_tokens = r.json()
        assert new_tokens["access_token"] != bearer_tokens["access_token"]
        assert new_tokens["refresh_token"] != bearer_tokens["refresh_token"]


class TestBearerRequestVerifyToken:
    async def test_existing_user(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/request-verify-token",
            json={"email": DEFAULT_EMAIL},
        )
        assert r.status_code == 202

    async def test_nonexistent_user_does_not_leak(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/request-verify-token",
            json={"email": "nobody@test.com"},
        )
        assert r.status_code == 202


class TestBearerVerify:
    async def test_invalid_token(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/verify",
            json={"token": "invalid.token.value"},
        )
        assert r.status_code == 400


class TestBearerForgotPassword:
    async def test_existing_user(self, client: AsyncClient, registered_user: dict):
        r = await client.post(
            "/api/auth/bearer/forgot-password",
            json={"email": DEFAULT_EMAIL},
        )
        assert r.status_code == 202

    async def test_nonexistent_user_does_not_leak(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/forgot-password",
            json={"email": "nobody@test.com"},
        )
        assert r.status_code == 202


class TestBearerResetPassword:
    async def test_invalid_token(self, client: AsyncClient):
        r = await client.post(
            "/api/auth/bearer/reset-password",
            json={"token": "invalid.token.value", "password": "NewPass123!"},
        )
        assert r.status_code == 400
