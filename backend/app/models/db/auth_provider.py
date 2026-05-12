"""AuthProvider ORM model — links authentication identities to a User."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ProviderType(str, Enum):
    """Supported authentication provider types."""
    password = "password"
    google = "google"
    microsoft = "microsoft"


class AuthProvider(SQLModel, table=True):
    """
    One row per (user, provider) combination.

    For the 'password' provider, hashed_credential holds the bcrypt/argon2 hash.
    For OAuth providers, provider_user_id holds the external identity and
    hashed_credential is NULL.
    """
    __tablename__ = "auth_providers"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    provider: ProviderType = Field(index=True)
    # External identity — email for password, OAuth subject for OAuth providers.
    provider_user_id: str = Field(index=True, max_length=255)
    # Only populated for the 'password' provider; never exposed in responses.
    hashed_credential: Optional[str] = Field(default=None)

    # Failed login attempt tracking for account lockout.
    failed_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # ── relationships ─────────────────────────────────────────────────────
    user: Optional["User"] = Relationship(back_populates="auth_providers")
