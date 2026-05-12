"""Database ORM models — import all so SQLModel metadata is fully populated."""
from .user import User
from .auth_provider import AuthProvider, ProviderType
from .deal import Deal, DealStatus
from .deal_verdict import DealVerdict
from .report import Report

__all__ = [
    "User",
    "AuthProvider",
    "ProviderType",
    "Deal",
    "DealStatus",
    "DealVerdict",
    "Report",
]
