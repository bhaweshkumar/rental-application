import pytest
from src.logic.data_integration import DataSourceManager

def test_manager_with_no_api_key():
    """Tests that the manager handles a missing API key gracefully."""
    manager = DataSourceManager(settings={})
    result = manager.get_property_data("123 Main St")
    assert "error" in result
    assert "API key not configured" in result["error"]

def test_get_property_data_success(mocker):
    """Tests a successful API call using a mock."""
    # 1. Setup
    api_key = "fake_api_key"
    address = "1600 Amphitheatre Parkway, Mountain View, CA"
    settings = {"realty_mole_api_key": api_key}
    manager = DataSourceManager(settings=settings)

    # Mock the response from requests.get
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"property": "details"}
    mock_get = mocker.patch("requests.get", return_value=mock_response)

    # 2. Execute
    result = manager.get_property_data(address)

    # 3. Assert
    # Check that requests.get was called correctly
    expected_url = f"https://realtymole-rental-estimate-v1.p.rapidapi.com/rentalPrice?address={address.replace(' ', '%20').replace(',', '%2C')}"
    mock_get.assert_called_once_with(
        expected_url,
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "realtymole-rental-estimate-v1.p.rapidapi.com",
        },
    )
    # Check that the result is the mocked JSON
    assert result == {"property": "details"}

def test_get_property_data_api_error(mocker):
    """Tests handling of a non-200 API response."""
    api_key = "fake_api_key"
    address = "123 Main St"
    settings = {"realty_mole_api_key": api_key}
    manager = DataSourceManager(settings=settings)

    mock_response = mocker.Mock()
    mock_response.status_code = 403 # Forbidden
    mock_response.reason = "Forbidden"
    mocker.patch("requests.get", return_value=mock_response)

    result = manager.get_property_data(address)

    assert "error" in result
    assert "API Error: 403 Forbidden" in result["error"]