from urllib.parse import quote

import requests


class DataSourceManager:
    """
    Acts as a data abstraction layer for sourcing property data from external APIs.
    """

    def __init__(self, settings: dict):
        self.api_key = settings.get("realty_mole_api_key")
        self.base_url = "https://realtymole-rental-estimate-v1.p.rapidapi.com/rentalPrice"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "realtymole-rental-estimate-v1.p.rapidapi.com",
        }

    def get_property_data(self, address: str) -> dict:
        """Fetches property data for a given address from the configured API provider."""
        if not self.api_key:
            return {"error": "API key not configured. Please add it in the Settings page."}

        try:
            encoded_address = quote(address)
            url = f"{self.base_url}?address={encoded_address}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()

            return {"error": f"API Error: {response.status_code} {response.reason}"}
        except requests.exceptions.RequestException as exc:
            return {"error": f"Network error: {exc}"}
