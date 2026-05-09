import json


def save_settings(settings: dict, filepath: str):
    """Saves a settings dictionary to a JSON file."""
    with open(filepath, "w") as file:
        json.dump(settings, file, indent=4)


def load_settings(filepath: str) -> dict:
    """Loads a settings dictionary from a JSON file."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
