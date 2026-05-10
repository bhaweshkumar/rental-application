import pytest
from rental_platform.services.settings_service import save_settings, load_settings

def test_save_and_load_settings(tmp_path):
    """Tests that settings can be saved to and loaded from a JSON file."""
    settings_to_save = {"realty_mole_api_key": "test_key_123"}
    filepath = tmp_path / "config.json"

    save_settings(settings_to_save, str(filepath))

    assert filepath.exists()

    loaded_settings = load_settings(str(filepath))

    assert loaded_settings == settings_to_save

def test_load_settings_non_existent_file():
    """Tests that loading from a non-existent file returns an empty dict."""
    loaded_settings = load_settings("non_existent_config.json")
    assert loaded_settings == {}