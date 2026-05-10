import pytest
from dataclasses import asdict
from rental_platform.services.brrrr_service import calculate_brrrr_metrics
from rental_platform.models import BrrrrMetrics

# Test cases: (purchase_price, total_rehab_budget, arv, refi_ltv_pct, expected_metrics)
test_cases = [
    # Scenario 1: Positive equity capture and positive cash out
    (200000, 50000, 350000, 75, BrrrrMetrics(all_in_cost=250000, equity_capture=100000, refi_loan_amount=262500, cash_out_proceeds=12500)),
    # Scenario 2: Positive equity capture but cash left in deal (negative cash out)
    (200000, 50000, 300000, 75, BrrrrMetrics(all_in_cost=250000, equity_capture=50000, refi_loan_amount=225000, cash_out_proceeds=-25000)),
    # Scenario 3: Zero equity capture and cash left in deal
    (250000, 50000, 300000, 80, BrrrrMetrics(all_in_cost=300000, equity_capture=0, refi_loan_amount=240000, cash_out_proceeds=-60000)),
    # Scenario 4: Zero rehab budget
    (250000, 0, 300000, 75, BrrrrMetrics(all_in_cost=250000, equity_capture=50000, refi_loan_amount=225000, cash_out_proceeds=-25000)),
    # Scenario 5: Zero ARV (should handle gracefully)
    (100000, 20000, 0, 75, BrrrrMetrics(all_in_cost=120000, equity_capture=-120000, refi_loan_amount=0, cash_out_proceeds=-120000)),
]

@pytest.mark.parametrize("purchase_price, total_rehab_budget, arv, refi_ltv_pct, expected", test_cases)
def test_calculate_brrrr_metrics(purchase_price, total_rehab_budget, arv, refi_ltv_pct, expected):
    """Tests the calculate_brrrr_metrics function for various scenarios."""
    result = calculate_brrrr_metrics(purchase_price, total_rehab_budget, arv, refi_ltv_pct)
    
    assert asdict(result) == pytest.approx(asdict(expected))