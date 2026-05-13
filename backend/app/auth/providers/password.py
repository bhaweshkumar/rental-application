from passlib.context import CryptContext

from app.config import get_settings
from .base import AuthProvider

settings = get_settings()

_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")


class PasswordProvider(AuthProvider):
    provider_name = "password"

    def __init__(self, algorithm: str | None = None) -> None:
        self.algorithm = algorithm or settings.auth_hash_algorithm
        if self.algorithm not in _context.schemes():
            self.algorithm = "bcrypt"

    def hash_credential(self, credential: str) -> str:
        return _context.hash(credential, scheme=self.algorithm)

    def verify_credential(self, credential: str, stored: str) -> bool:
        return _context.verify(credential, stored)
