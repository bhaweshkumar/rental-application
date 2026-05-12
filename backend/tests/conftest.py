"""Shared pytest fixtures for backend tests."""
import os
import pytest
from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

# Override database URL to in-memory SQLite before any app module runs.
os.environ["DATABASE_URL"] = "sqlite://"

# Import app AFTER setting the env var so config picks up the in-memory URL.
import app.models.db  # noqa: F401, E402  — registers all models with SQLModel metadata
from app.main import app as fastapi_app  # noqa: E402


@pytest.fixture(name="engine", scope="session")
def engine_fixture():
    """Create a fresh in-memory SQLite engine shared for the test session."""
    _engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(_engine)
    yield _engine
    SQLModel.metadata.drop_all(_engine)


@pytest.fixture(name="db")
def db_fixture(engine) -> Generator[Session, None, None]:
    """Yield a database session that is rolled back after each test."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture(name="client")
def client_fixture(engine) -> Generator[TestClient, None, None]:
    """FastAPI TestClient wired to the in-memory test engine."""
    from app.database import get_db

    def override_get_db():
        with Session(engine) as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()
