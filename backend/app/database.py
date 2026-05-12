"""Database engine, session factory, and FastAPI dependency."""
from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

settings = get_settings()

# connect_args is SQLite-specific — allows multi-threaded access.
_connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    echo=settings.debug,
)


def create_db_and_tables() -> None:
    """Create all tables defined by SQLModel metadata.

    Called at application startup. Safe to call multiple times (no-op if
    tables already exist). Alembic handles incremental migrations in
    production; this function is retained for test isolation.
    """
    # Importing here ensures all models are registered with SQLModel.metadata
    # before create_all() is called.
    import app.models.db  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency — yields a database session per request."""
    with Session(engine) as session:
        yield session
