import pytest
from rental_platform.services.tax_service import calculate_depreciation
from rental_platform.models import TaxOptimizationInputs, TaxOptimizationOutputs

# Depreciable basis (Purchase Price - Land Value). Assume 80% for this test.
PURCHASE_PRICE = 500000
IMPROVEMENT_BASIS = PURCHASE_PRICE * 0.8 # A common rule of thumb is 80% improvement, 20% land.
RESIDENTIAL_DEPRECIATION_YEARS = 27.5

def test_calculate_standard_depreciation():
    """Tests depreciation without cost segregation."""
    inputs = TaxOptimizationInputs(enable_cost_segregation=False)
    outputs = calculate_depreciation(IMPROVEMENT_BASIS, RESIDENTIAL_DEPRECIATION_YEARS, inputs)

    assert outputs.year_1_bonus_depreciation == 0
    # Standard SL depreciation for year 1
    expected_std_dep = IMPROVEMENT_BASIS / RESIDENTIAL_DEPRECIATION_YEARS
    assert outputs.total_year_1_depreciation == pytest.approx(expected_std_dep)
    assert outputs.annual_std_depreciation_after_y1 == pytest.approx(expected_std_dep)

def test_calculate_accelerated_depreciation_with_cost_seg():
    """Tests depreciation with cost segregation and 100% bonus depreciation."""
    inputs = TaxOptimizationInputs(
        enable_cost_segregation=True,
        cost_seg_5_year_pct=20, # 20% of basis is 5-year property
        cost_seg_15_year_pct=10, # 10% of basis is 15-year property
    )
    outputs = calculate_depreciation(IMPROVEMENT_BASIS, RESIDENTIAL_DEPRECIATION_YEARS, inputs)

    # Calculate expected bonus depreciation
    cost_seg_5_year_value = IMPROVEMENT_BASIS * (inputs.cost_seg_5_year_pct / 100.0)
    cost_seg_15_year_value = IMPROVEMENT_BASIS * (inputs.cost_seg_15_year_pct / 100.0)
    expected_bonus_depreciation = cost_seg_5_year_value + cost_seg_15_year_value
    assert outputs.year_1_bonus_depreciation == pytest.approx(expected_bonus_depreciation)

    # Calculate remaining basis and its depreciation
    remaining_basis = IMPROVEMENT_BASIS - expected_bonus_depreciation
    expected_std_dep_on_remainder = remaining_basis / RESIDENTIAL_DEPRECIATION_YEARS
    assert outputs.year_1_standard_depreciation == pytest.approx(expected_std_dep_on_remainder)
    
    # Total Y1 depreciation
    expected_total_y1_dep = expected_bonus_depreciation + expected_std_dep_on_remainder
    assert outputs.total_year_1_depreciation == pytest.approx(expected_total_y1_dep)

    # Ongoing depreciation for years 2+
    assert outputs.annual_std_depreciation_after_y1 == pytest.approx(expected_std_dep_on_remainder)
    assert outputs.remaining_basis_for_std_dep == pytest.approx(remaining_basis)