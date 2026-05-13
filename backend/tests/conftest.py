"""Shared pytest fixtures for backend tests."""
import os
import pytest
from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Override database URL to in-memory SQLite BEFORE any app module runs.
os.environ["DATABASE_URL"] = "sqlite://"

# Import models first to register them with SQLModel.metadata
import app.models.db  # noqa: F401, E402

# Now import and patch app.database BEFORE importing create_app
import app.database  # noqa: E402
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False, "uri": True},
    poolclass=__import__("sqlalchemy.pool", fromlist=["StaticPool"]).StaticPool,
)
SQLModel.metadata.create_all(test_engine)
app.database.engine = test_engine

# NOW import create_app which will use our patched engine
from app.main import create_app  # noqa: E402


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    """Return the test engine that was already created and patched."""
    return test_engine


@pytest.fixture(name="db")
def db_fixture() -> Generator[Session, None, None]:
    """Yield a database session that is rolled back after each test."""
    with Session(test_engine) as session:
        yield session
        session.rollback()


@pytest.fixture(name="client")
def client_fixture() -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the test engine."""
    from app.database import get_db

    def override_get_db():
        with Session(test_engine) as session:
            yield session

    fastapi_app = create_app()
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
