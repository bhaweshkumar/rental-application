"""Deal ORM model."""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional, TYPE_CHECKING

from sqlmodel import Column, Field, JSON, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User
    from .deal_verdict import DealVerdict
    from .report import Report


class DealStatus(str, Enum):
    """Lifecycle status of a deal."""
    analysis = "analysis"
    under_contract = "under_contract"
    closed = "closed"
    rejected = "rejected"
    deleted = "deleted"  # soft-delete sentinel


class Deal(SQLModel, table=True):
    """
    Persists a single rental deal analysis.

    deal_data (JSON) stores the full DealProfile payload from
    rental_platform/models/domain.py, enabling zero-schema-migration during
    the transition from Streamlit to the React frontend.
    """
    __tablename__ = "deals"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)

    # Quick-access columns for listing/filtering (denormalised from deal_data)
    address: Optional[str] = Field(default=None, max_length=500)
    asset_type: Optional[str] = Field(default=None, max_length=100)
    status: DealStatus = Field(default=DealStatus.analysis, index=True)

    # Full DealProfile payload serialised to JSON
    deal_data: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # ── relationships ─────────────────────────────────────────────────────
    user: Optional["User"] = Relationship(back_populates="deals")
    verdicts: list["DealVerdict"] = Relationship(back_populates="deal")
    reports: list["Report"] = Relationship(back_populates="deal")
