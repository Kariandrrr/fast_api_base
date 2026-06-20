import asyncio
from contextlib import AsyncExitStack
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.app import main_app
from app.core.config.main_config import Settings
from app.core.models import Base, db_helper, redis_helper

DEFAULT_EMAIL = "owner@test.com"
DEFAULT_PASSWORD = "Test1234!"
DEFAULT_DISPLAY_NAME = "Test Owner"

_test_settings = Settings(_env_file=(".env", ".env.test"))
TEST_DB_URL = str(_test_settings.db.pg.url)

test_engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
test_session_factory = async_sessionmaker(
    test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def _create():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _drop():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(_create())
    yield
    asyncio.run(_drop())


@pytest.fixture(autouse=True)
async def clean_tables():
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    await redis_helper.pool.disconnect()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_session():
        async with test_session_factory() as s:
            yield s

    main_app.dependency_overrides[db_helper.session_getter] = override_session
    async with AsyncClient(
        transport=ASGITransport(app=main_app), base_url="http://test"
    ) as ac:
        yield ac
    main_app.dependency_overrides.clear()


@pytest.fixture
async def registered_user(client: AsyncClient) -> dict:
    r = await client.post(
        "/api/auth/cookie/register",
        json={"email": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD, "display_name": DEFAULT_DISPLAY_NAME},
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
async def auth_client(client: AsyncClient, registered_user: dict) -> AsyncClient:
    _ = registered_user
    r = await client.post(
        "/api/auth/cookie/login",
        data={"username": DEFAULT_EMAIL, "password": DEFAULT_PASSWORD},
    )
    assert r.status_code == 204
    return client


@pytest.fixture
async def org(auth_client: AsyncClient) -> dict:
    r = await auth_client.post("/api/orgs", json={"name": "Test Org"})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
async def project(auth_client: AsyncClient, org: dict) -> dict:
    r = await auth_client.post(
        f"/api/orgs/{org['id']}/projects",
        json={"name": "Test Project"},
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
async def task(auth_client: AsyncClient, org: dict, project: dict) -> dict:
    r = await auth_client.post(
        f"/api/orgs/{org['id']}/projects/{project['id']}/tasks",
        json={"title": "Test Task", "priority": "medium"},
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
async def make_member(auth_client: AsyncClient, org: dict) -> AsyncGenerator:
    """Factory: invite + register + login + accept. Returns AsyncClient for the new member."""
    created: list[tuple[AsyncClient, AsyncExitStack]] = []

    async def _make(email: str, role: str = "employee", position: str = "Developer") -> AsyncClient:
        r = await auth_client.post(
            f"/api/orgs/{org['id']}/invite",
            json={"email": email, "role": role, "position": position},
        )
        assert r.status_code == 201
        token = r.json()["token"]

        stack = AsyncExitStack()
        ac: AsyncClient = await stack.enter_async_context(
            AsyncClient(transport=ASGITransport(app=main_app), base_url="http://test")
        )
        created.append((ac, stack))

        await ac.post(
            "/api/auth/cookie/register",
            json={"email": email, "password": DEFAULT_PASSWORD, "display_name": "Test Member"},
        )
        await ac.post(
            "/api/auth/cookie/login",
            data={"username": email, "password": DEFAULT_PASSWORD},
        )
        await ac.post(f"/api/invitations/{token}/accept")
        return ac

    yield _make

    for _, stack in created:
        await stack.aclose()
