"""RefreshToken ORM model for persisted refresh token revocation."""
import hashlib
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(max_length=128, index=True)
    expires_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="refresh_tokens")

    @classmethod
    def hash_token(cls, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()
