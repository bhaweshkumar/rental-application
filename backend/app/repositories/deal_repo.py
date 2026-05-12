"""DealRepository — data access for the Deal model."""
from typing import Optional, Sequence

from sqlmodel import Session, select

from app.models.db.deal import Deal, DealStatus
from app.models.db.deal_verdict import DealVerdict
from .base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    model = Deal

    def list_by_user_id(
        self,
        db: Session,
        *,
        user_id: str,
        exclude_deleted: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[Deal]:
        """Return all deals owned by *user_id*, newest first.

        By default soft-deleted deals (status='deleted') are excluded.
        """
        stmt = (
            select(Deal)
            .where(Deal.user_id == user_id)
            .order_by(Deal.created_at.desc())  # type: ignore[union-attr]
            .offset(offset)
            .limit(limit)
        )
        if exclude_deleted:
            stmt = stmt.where(Deal.status != DealStatus.deleted)
        return db.exec(stmt).all()

    def get_by_id_for_user(
        self,
        db: Session,
        *,
        deal_id: str,
        user_id: str,
    ) -> Optional[Deal]:
        """Return the deal only if it belongs to *user_id*."""
        stmt = (
            select(Deal)
            .where(Deal.id == deal_id, Deal.user_id == user_id)
            .where(Deal.status != DealStatus.deleted)
        )
        return db.exec(stmt).first()

    def get_with_verdicts(
        self,
        db: Session,
        *,
        deal_id: str,
    ) -> tuple[Optional[Deal], Sequence[DealVerdict]]:
        """Return a deal and all its associated verdicts."""
        deal = db.get(Deal, deal_id)
        if deal is None:
            return None, []
        stmt = (
            select(DealVerdict)
            .where(DealVerdict.deal_id == deal_id)
            .order_by(DealVerdict.computed_at.desc())  # type: ignore[union-attr]
        )
        verdicts = db.exec(stmt).all()
        return deal, verdicts

    def soft_delete(self, db: Session, *, db_obj: Deal) -> Deal:
        """Mark a deal as deleted without removing the row."""
        return self.update(db, db_obj=db_obj, updates={"status": DealStatus.deleted})


deal_repo = DealRepository()
