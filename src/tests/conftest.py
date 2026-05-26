from __future__ import annotations

import os

import psycopg2
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

TEST_DB_NAME = "diploma_project_test"

os.environ["DB_HOST"] = os.getenv("DB_HOST", "127.0.0.1")
os.environ["DB_PORT"] = os.getenv("DB_PORT", "5432")
os.environ["DB_NAME"] = TEST_DB_NAME
os.environ["DB_USER"] = os.getenv("DB_USER", "postgres")
os.environ["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "123456")
os.environ["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "HqHti873210ufhiHOI8yGFYU7-8Y87g89t78G9h8gt6rYUVugdwlnclo",
)
os.environ["ALGORITHM"] = os.getenv("ALGORITHM", "HS256")
os.environ["TWILIO_AUTH_TOKEN"] = os.getenv("TWILIO_AUTH_TOKEN", "test-token")
os.environ["TWILIO_ACCOUNT_SID"] = os.getenv("TWILIO_ACCOUNT_SID", "test-sid")
os.environ["TWILIO_PHONE_NUMBER"] = os.getenv("TWILIO_PHONE_NUMBER", "+10000000000")
os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "127.0.0.1")
os.environ["REDIS_PORT"] = os.getenv("REDIS_PORT", "6379")
os.environ["REDIS_PASSWORD"] = os.getenv("REDIS_PASSWORD", "")
os.environ["DG_API_KEY"] = os.getenv("DG_API_KEY", "test-dg-key")


def _ensure_test_database() -> None:
    connection = psycopg2.connect(
        dbname="postgres",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )
    connection.autocommit = True

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,))
            if cursor.fetchone() is None:
                cursor.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        connection.close()


_ensure_test_database()

from src.main import app  # noqa: E402
from src.shared.configurations.database import Base, async_session_maker, engine  # noqa: E402
import src.shared.models.model  # noqa: F401,E402
from src.shared.service.coordinate_service import CoordinatesService  # noqa: E402
import src.modules.users.service as users_service_module  # noqa: E402
from src.tests.factories import TestFactory  # noqa: E402


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        if conn.dialect.name == "postgresql":
            autocommit_conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await autocommit_conn.exec_driver_sql("ALTER TYPE role ADD VALUE IF NOT EXISTS 'owner'")

    yield
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_database(prepare_database):
    table_names = ", ".join(f'"{table.name}"' for table in reversed(Base.metadata.sorted_tables))
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def sms_code_store() -> dict[str, str]:
    return {}


@pytest.fixture(autouse=True)
def patch_external_services(monkeypatch: pytest.MonkeyPatch, sms_code_store: dict[str, str]):
    async def fake_get_coordinates(_cls, address: str) -> tuple[float, float]:
        seed = sum(ord(char) for char in address)
        return round(seed / 100, 4), round(seed / 80, 4)

    async def fake_set_code(phone: str, code: str):
        sms_code_store[phone] = code

    async def fake_get_code(phone: str):
        return sms_code_store.get(phone)

    async def fake_delete_code(phone: str):
        sms_code_store.pop(phone, None)

    async def fake_send_sms(_phone: str, _body: str):
        return True

    monkeypatch.setattr(CoordinatesService, "get_coordinates_2gis", classmethod(fake_get_coordinates))
    monkeypatch.setattr(users_service_module, "set_code", fake_set_code)
    monkeypatch.setattr(users_service_module, "get_code", fake_get_code)
    monkeypatch.setattr(users_service_module, "delete_code", fake_delete_code)
    monkeypatch.setattr(users_service_module, "send_sms_via_twilio", fake_send_sms)


@pytest_asyncio.fixture
async def client(prepare_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client


@pytest.fixture
def factory() -> TestFactory:
    return TestFactory()


@pytest_asyncio.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session
