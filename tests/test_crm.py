import pytest
from rental_platform.services.crm_service import save_deals, load_deals
from rental_platform.models import DealProfile, PropertyDetails

def test_save_and_load_deals(tmp_path):
    """Tests that deals can be saved to and loaded from a JSON file."""
    # 1. Create some sample deals
    deal1 = DealProfile(property_details=PropertyDetails(address="123 Main St"))
    deal2 = DealProfile(property_details=PropertyDetails(address="456 Oak Ave"))
    deals_to_save = [deal1, deal2]

    filepath = tmp_path / "deals.json"

    # 2. Save the deals
    save_deals(deals_to_save, str(filepath))

    # 3. Check if file was created and has content
    assert filepath.exists()
    assert filepath.read_text() != ""

    # 4. Load the deals back
    loaded_deals = load_deals(str(filepath))

    # 5. Assert the loaded deals match the original ones
    assert len(loaded_deals) == 2
    assert loaded_deals[0].property_details.address == "123 Main St"
    assert loaded_deals[1].property_details.address == "456 Oak Ave"
    assert loaded_deals[0].id == deal1.id

def test_load_deals_non_existent_file():
    """Tests that loading from a non-existent file returns an empty list."""
    loaded_deals = load_deals("non_existent_file.json")
    assert loaded_deals == []