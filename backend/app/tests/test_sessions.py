import pytest
from httpx import AsyncClient, ASGITransport

from app.app import main_app

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


class TestListSessions:
    async def test_one_session_after_login(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        r = await client.get("/api/sessions", headers=headers)
        assert r.status_code == 200
        sessions = r.json()
        assert len(sessions) == 1
        s = sessions[0]
        assert "session_id" in s
        assert "device" in s
        assert "browser" in s
        assert "os" in s
        assert "ip" in s
        assert "created_at" in s
        assert "last_active" in s
        assert s["is_current"] is True

    async def test_multiple_sessions(self, client: AsyncClient, registered_user: dict):
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

        headers = {"Authorization": f"Bearer {tokens1['access_token']}"}
        r = await client.get("/api/sessions", headers=headers)
        assert r.status_code == 200
        sessions = r.json()
        assert len(sessions) == 2

        current_sessions = [s for s in sessions if s["is_current"]]
        other_sessions = [s for s in sessions if not s["is_current"]]
        assert len(current_sessions) == 1
        assert len(other_sessions) == 1

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.get("/api/sessions")
        assert r.status_code == 401

    async def test_cookie_session(self, auth_client: AsyncClient):
        r = await auth_client.get("/api/sessions")
        assert r.status_code == 200
        sessions = r.json()
        assert len(sessions) == 1
        assert sessions[0]["is_current"] is True


class TestRevokeSession:
    async def test_revoke_other_session(self, client: AsyncClient, registered_user: dict):
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
        sessions = (await client.get("/api/sessions", headers=headers1)).json()
        other = [s for s in sessions if not s["is_current"]][0]

        r = await client.delete(
            f"/api/sessions/{other['session_id']}", headers=headers1
        )
        assert r.status_code == 204

        sessions_after = (await client.get("/api/sessions", headers=headers1)).json()
        assert len(sessions_after) == 1
        assert sessions_after[0]["is_current"] is True

    async def test_revoked_session_tokens_rejected(self, client: AsyncClient, registered_user: dict):
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
        headers2 = {"Authorization": f"Bearer {tokens2['access_token']}"}

        sessions = (await client.get("/api/sessions", headers=headers1)).json()
        other = [s for s in sessions if not s["is_current"]][0]
        await client.delete(f"/api/sessions/{other['session_id']}", headers=headers1)

        r = await client.get("/api/users/me", headers=headers2)
        assert r.status_code == 401

    async def test_not_found(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        r = await client.delete("/api/sessions/nonexistent-id", headers=headers)
        assert r.status_code == 404

    async def test_unauthenticated(self, client: AsyncClient):
        r = await client.delete("/api/sessions/some-id")
        assert r.status_code == 401


class TestSessionLifecycle:
    async def test_session_deleted_on_logout(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        sessions_before = (await client.get("/api/sessions", headers=headers)).json()
        assert len(sessions_before) == 1

        await client.post(
            "/api/auth/bearer/logout",
            json={"refresh_token": bearer_tokens["refresh_token"]},
            headers=headers,
        )

        r2 = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        new_tokens = r2.json()
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        sessions_after = (await client.get("/api/sessions", headers=new_headers)).json()
        assert len(sessions_after) == 1
        assert sessions_after[0]["session_id"] != sessions_before[0]["session_id"]

    async def test_all_sessions_deleted_on_logout_all(self, client: AsyncClient, registered_user: dict):
        r1 = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        tokens1 = r1.json()
        await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )

        headers1 = {"Authorization": f"Bearer {tokens1['access_token']}"}
        sessions = (await client.get("/api/sessions", headers=headers1)).json()
        assert len(sessions) == 2

        await client.post("/api/auth/bearer/logout-all", headers=headers1)

        r3 = await client.post(
            "/api/auth/bearer/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        new_tokens = r3.json()
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        sessions_after = (await client.get("/api/sessions", headers=new_headers)).json()
        assert len(sessions_after) == 1

    async def test_refresh_updates_session(self, client: AsyncClient, bearer_tokens: dict):
        headers = {"Authorization": f"Bearer {bearer_tokens['access_token']}"}
        sessions_before = (await client.get("/api/sessions", headers=headers)).json()

        r = await client.post(
            "/api/auth/bearer/refresh",
            json={
                "access_token": bearer_tokens["access_token"],
                "refresh_token": bearer_tokens["refresh_token"],
            },
        )
        assert r.status_code == 200
        new_tokens = r.json()
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}

        sessions_after = (await client.get("/api/sessions", headers=new_headers)).json()
        assert len(sessions_after) == 1
        assert sessions_after[0]["session_id"] == sessions_before[0]["session_id"]
        assert sessions_after[0]["last_active"] >= sessions_before[0]["last_active"]

    async def test_cookie_session_deleted_on_logout(self, auth_client: AsyncClient):
        sessions_before = (await auth_client.get("/api/sessions")).json()
        assert len(sessions_before) == 1

        await auth_client.post("/api/auth/cookie/logout")

        await auth_client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        sessions_after = (await auth_client.get("/api/sessions")).json()
        assert len(sessions_after) == 1
        assert sessions_after[0]["session_id"] != sessions_before[0]["session_id"]

    async def test_cookie_revoke_other_session(self, client: AsyncClient, registered_user: dict):
        await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        async with AsyncClient(
            transport=ASGITransport(app=main_app), base_url="http://test"
        ) as client2:
            await client2.post(
                "/api/auth/cookie/login",
                data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
            )
            r_before = await client2.get("/api/users/me")
            assert r_before.status_code == 200

            sessions = (await client.get("/api/sessions")).json()
            other = [s for s in sessions if not s["is_current"]][0]
            await client.delete(f"/api/sessions/{other['session_id']}")

            r_after = await client2.get("/api/users/me")
            assert r_after.status_code == 401

    async def test_cookie_all_sessions_deleted_on_logout_all(self, client: AsyncClient, registered_user: dict):
        await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        async with AsyncClient(
            transport=ASGITransport(app=main_app), base_url="http://test"
        ) as client2:
            await client2.post(
                "/api/auth/cookie/login",
                data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
            )
            sessions = (await client.get("/api/sessions")).json()
            assert len(sessions) == 2

            await client.post("/api/auth/cookie/logout-all")

            r_after = await client2.get("/api/users/me")
            assert r_after.status_code == 401

        await client.post(
            "/api/auth/cookie/login",
            data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
        )
        sessions_after = (await client.get("/api/sessions")).json()
        assert len(sessions_after) == 1

    async def test_cookie_refresh_preserves_session(self, auth_client: AsyncClient):
        sessions_before = (await auth_client.get("/api/sessions")).json()
        assert len(sessions_before) == 1

        await auth_client.post("/api/auth/cookie/refresh")

        sessions_after = (await auth_client.get("/api/sessions")).json()
        assert len(sessions_after) == 1
        assert sessions_after[0]["session_id"] == sessions_before[0]["session_id"]
        assert sessions_after[0]["last_active"] >= sessions_before[0]["last_active"]