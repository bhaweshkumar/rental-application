"""Generic BaseRepository — typed CRUD layer over SQLModel."""
from typing import Any, Generic, Optional, Sequence, TypeVar

from sqlmodel import Session, SQLModel, select

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(Generic[ModelT]):
    """
    Generic repository that wraps common database operations for a SQLModel
    table model. Subclasses inject the concrete model class via ``model``.

    All methods take a ``db: Session`` argument rather than storing one,
    keeping the repository stateless and safe for dependency injection.
    """

    model: type[ModelT]

    # ── create ────────────────────────────────────────────────────────────
    def create(self, db: Session, *, obj: ModelT) -> ModelT:
        """Persist a new instance and return the refreshed record."""
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    # ── read ──────────────────────────────────────────────────────────────
    def get_by_id(self, db: Session, *, record_id: str) -> Optional[ModelT]:
        """Return the record with *record_id* or None."""
        return db.get(self.model, record_id)

    def list_all(self, db: Session, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        """Return up to *limit* records starting at *offset*."""
        stmt = select(self.model).offset(offset).limit(limit)
        return db.exec(stmt).all()

    def list_for_user(
        self,
        db: Session,
        *,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Sequence[ModelT]:
        """Return records belonging to *user_id*.

        Assumes the model has a ``user_id`` column. Subclasses that target
        models without this column should override or ignore this method.
        """
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)  # type: ignore[attr-defined]
            .offset(offset)
            .limit(limit)
        )
        return db.exec(stmt).all()

    # ── update ────────────────────────────────────────────────────────────
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelT,
        updates: dict[str, Any],
    ) -> ModelT:
        """Apply *updates* to *db_obj* and persist."""
        for field, value in updates.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # ── delete ────────────────────────────────────────────────────────────
    def delete(self, db: Session, *, db_obj: ModelT) -> None:
        """Delete *db_obj* from the database."""
        db.delete(db_obj)
        db.commit()
