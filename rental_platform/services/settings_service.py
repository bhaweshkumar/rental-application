"""Settings persistence service."""
import json


def save_settings(settings: dict, filepath: str) -> None:
    """Saves a settings dictionary to a JSON file."""
    with open(filepath, "w") as f:
        json.dump(settings, f, indent=4)


def load_settings(filepath: str) -> dict:
    """Loads a settings dictionary from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
