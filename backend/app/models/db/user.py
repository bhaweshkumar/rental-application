"""User ORM model."""
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .auth_provider import AuthProvider
    from .deal import Deal
    from .report import Report


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    email: str = Field(unique=True, index=True, max_length=255)
    display_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # ── relationships ─────────────────────────────────────────────────────
    auth_providers: list["AuthProvider"] = Relationship(back_populates="user")
    deals: list["Deal"] = Relationship(back_populates="user")
    reports: list["Report"] = Relationship(back_populates="user")
