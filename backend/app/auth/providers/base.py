from abc import ABC, abstractmethod


class AuthProvider(ABC):
    provider_name: str

    @abstractmethod
    def verify_credential(self, credential: str, stored: str) -> bool:
        """Verify a plaintext credential against the stored representation."""

    @abstractmethod
    def hash_credential(self, credential: str) -> str:
        """Return a cryptographic hash for the provided credential."""
