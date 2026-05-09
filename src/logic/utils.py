from typing import List, Any

def get_safe_index(options: List[Any], value: Any, default: int = 0) -> int:
    """
    Safely finds the index of a value in a list.
    Returns the default index (0) if the value is not found.
    """
    try:
        return options.index(value)
    except ValueError:
        return default