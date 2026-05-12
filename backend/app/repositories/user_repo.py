"""UserRepository — data access for the User model."""
from typing import Optional

from sqlmodel import Session, select

from app.models.db.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Return the user with the given email, or None."""
        stmt = select(User).where(User.email == email)
        return db.exec(stmt).first()

    def get_active_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Return only active users matching the email."""
        stmt = select(User).where(User.email == email, User.is_active.is_(True))
        return db.exec(stmt).first()


user_repo = UserRepository()
