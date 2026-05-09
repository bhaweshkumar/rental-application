import pytest
from src.logic.rehab import calculate_rehab_costs

# To run these tests, install pytest (`pip install pytest`) and run `pytest` from the root directory.

@pytest.mark.parametrize(
    "sq_ft, rehab_level, contingency_pct, expected_base, expected_contingency, expected_total",
    [
        (1000, "Light (Cosmetic/Paint)", 10, 20000, 2000, 22000),
        (2000, "Medium (Systems/Plumbing)", 15, 75000, 11250, 86250),
        (1500, "Heavy (Gut/Studs)", 20, 97500, 19500, 117000),
        (1000, "None", 10, 0, 0, 0),
        (1200, "Invalid Level", 10, 0, 0, 0), # Test handling of invalid rehab level
        (0, "Light (Cosmetic/Paint)", 10, 0, 0, 0), # Test zero square footage
    ],
)
def test_calculate_rehab_costs(sq_ft, rehab_level, contingency_pct, expected_base, expected_contingency, expected_total):
    """Tests the calculate_rehab_costs function with various inputs."""
    base_cost, contingency_amt, total_budget = calculate_rehab_costs(sq_ft, rehab_level, contingency_pct)

    assert base_cost == pytest.approx(expected_base)
    assert contingency_amt == pytest.approx(expected_contingency)
    assert total_budget == pytest.approx(expected_total)