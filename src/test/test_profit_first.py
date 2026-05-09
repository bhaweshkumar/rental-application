import pytest
from dataclasses import asdict
from src.logic.profit_first import calculate_profit_first_allocations
from src.shared.models import ProfitFirstInputs, ProfitFirstOutputs

def test_calculate_profit_first_allocations():
    """Tests the calculation of cash sweeps based on Target Allocation Percentages."""
    gross_income = 5000.0
    taps = ProfitFirstInputs(
        profit_tap_pct=10,
        owners_pay_tap_pct=20,
        tax_tap_pct=15,
    )

    result = calculate_profit_first_allocations(gross_income, taps)

    expected_profit = 500.0
    expected_owners_pay = 1000.0
    expected_tax = 750.0
    expected_opex = 5000.0 - (expected_profit + expected_owners_pay + expected_tax)

    expected_outputs = ProfitFirstOutputs(
        profit_allocation=expected_profit,
        owners_pay_allocation=expected_owners_pay,
        tax_allocation=expected_tax,
        opex_allocation=expected_opex,
    )

    assert asdict(result) == pytest.approx(asdict(expected_outputs))

def test_calculate_profit_first_zero_income():
    """Tests with zero gross income."""
    gross_income = 0.0
    taps = ProfitFirstInputs(profit_tap_pct=10, owners_pay_tap_pct=20, tax_tap_pct=15)
    result = calculate_profit_first_allocations(gross_income, taps)
    expected_outputs = ProfitFirstOutputs(0.0, 0.0, 0.0, 0.0)
    assert asdict(result) == pytest.approx(asdict(expected_outputs))

def test_calculate_profit_first_total_allocation_exceeds_100():
    """Tests when TAPs exceed 100%, OpEx should be negative."""
    gross_income = 5000.0
    taps = ProfitFirstInputs(profit_tap_pct=50, owners_pay_tap_pct=50, tax_tap_pct=10)
    result = calculate_profit_first_allocations(gross_income, taps)
    expected_opex = 5000.0 - (2500.0 + 2500.0 + 500.0) # -500
    assert result.opex_allocation == pytest.approx(expected_opex)