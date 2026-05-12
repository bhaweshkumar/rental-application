"""Report ORM model — generated deal analysis documents."""
import uuid
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from sqlmodel import Column, Field, JSON, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User
    from .deal import Deal


class Report(SQLModel, table=True):
    """
    A generated report attached to a deal (e.g. deal summary, proforma export).

    payload stores the report content as a JSON document, enabling flexible
    report types without schema migrations.
    """
    __tablename__ = "reports"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    user_id: str = Field(foreign_key="users.id", index=True)
    deal_id: Optional[str] = Field(default=None, foreign_key="deals.id", index=True)

    # e.g. "deal_summary", "proforma", "brrrr_analysis"
    report_type: str = Field(max_length=100)

    # Full report payload stored as JSON
    payload: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))

    generated_at: datetime = Field(default_factory=datetime.utcnow)

    # ── relationships ─────────────────────────────────────────────────────
    user: Optional["User"] = Relationship(back_populates="reports")
    deal: Optional["Deal"] = Relationship(back_populates="reports")
