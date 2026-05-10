"""Input coercion and safe-lookup helpers."""
from typing import Any, List, Optional


def coerce_int(value: Any, *, minimum: int = 0, maximum: Optional[int] = None) -> int:
    """Safely coerces a value to int, clamped to [minimum, maximum]."""
    try:
        result = int(float(value))
    except (TypeError, ValueError):
        result = minimum
    result = max(result, minimum)
    if maximum is not None:
        result = min(result, maximum)
    return result


def coerce_float(value: Any, *, minimum: float = 0.0, maximum: Optional[float] = None) -> float:
    """Safely coerces a value to float, clamped to [minimum, maximum]."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = minimum
    result = max(result, minimum)
    if maximum is not None:
        result = min(result, maximum)
    return result


def get_safe_index(options: List[Any], value: Any, default: int = 0) -> int:
    """Returns the index of value in options, or default if not found."""
    try:
        return list(options).index(value)
    except ValueError:
        return default
