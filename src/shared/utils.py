"""Compatibility exports for shared utility helpers."""

try:
    from src.logic.utils import get_safe_index  # type: ignore
except ImportError:
    from logic.utils import get_safe_index  # type: ignore

__all__ = ["get_safe_index"]
