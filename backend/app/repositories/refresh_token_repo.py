from typing import Optional

from sqlmodel import Session, select

from app.models.db.refresh_token import RefreshToken
from .base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    model = RefreshToken

    def get_by_hash(self, db: Session, *, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return db.exec(stmt).first()

    def revoke(self, db: Session, *, db_obj: RefreshToken) -> RefreshToken:
        return self.update(db, db_obj=db_obj, updates={"revoked": True})


refresh_token_repo = RefreshTokenRepository()
