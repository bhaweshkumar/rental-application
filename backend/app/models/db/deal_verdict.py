"""DealVerdict ORM model — immutable snapshot of a computed verdict."""
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .deal import Deal


class DealVerdict(SQLModel, table=True):
    """
    Each time a user requests a verdict computation the result is snapshotted
    here, providing a full audit history of how a deal's analysis evolved.
    """
    __tablename__ = "deal_verdicts"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        index=True,
    )
    deal_id: str = Field(foreign_key="deals.id", index=True)

    # Verdict classification
    verdict_status: str = Field(max_length=20)  # "Pass" | "Caution" | "Fail"

    # Key financial metrics at the time of computation
    monthly_cash_flow: float = Field(default=0.0)
    dscr: float = Field(default=0.0)
    cap_rate: float = Field(default=0.0)
    cash_on_cash_return: float = Field(default=0.0)
    total_cash_required: float = Field(default=0.0)
    noi: float = Field(default=0.0)

    computed_at: datetime = Field(default_factory=datetime.utcnow)

    # ── relationships ─────────────────────────────────────────────────────
    deal: Optional["Deal"] = Relationship(back_populates="verdicts")
