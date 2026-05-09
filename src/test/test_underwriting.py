import pytest
from src.logic.underwriting import (
    calculate_noi,
    calculate_cap_rate,
    calculate_dscr,
    calculate_cash_on_cash,
    calculate_total_cash_invested,
)

# Test data based on a realistic scenario
ANNUAL_GROSS_RENT = 36000  # $3000/month
VACANCY_PCT = 5
OPEX_FIXED = 13680 # 40% of EGI (36000 * 0.95 * 0.40)
ANNUAL_DEBT_SERVICE = 17267.04 # From a $240k loan at 6% for 30 years
PURCHASE_PRICE = 300000
DOWN_PAYMENT = 60000
CLOSING_COSTS = 9000
REHAB_BUDGET = 25000

# Expected intermediate values
EXPECTED_EGI = ANNUAL_GROSS_RENT * (1 - (VACANCY_PCT / 100.0)) # 36000 * 0.95 = 34200
EXPECTED_NOI = EXPECTED_EGI - OPEX_FIXED # 34200 - 13680 = 20520
EXPECTED_TOTAL_CASH = DOWN_PAYMENT + CLOSING_COSTS + REHAB_BUDGET # 60000 + 9000 + 25000 = 94000

def test_calculate_total_cash_invested():
    total_cash = calculate_total_cash_invested(DOWN_PAYMENT, CLOSING_COSTS, REHAB_BUDGET)
    assert total_cash == pytest.approx(EXPECTED_TOTAL_CASH)

def test_calculate_noi():
    noi = calculate_noi(ANNUAL_GROSS_RENT, VACANCY_PCT, OPEX_FIXED)
    assert noi == pytest.approx(EXPECTED_NOI)

def test_calculate_cap_rate():
    cap_rate = calculate_cap_rate(EXPECTED_NOI, PURCHASE_PRICE)
    expected_cap_rate = (EXPECTED_NOI / PURCHASE_PRICE) * 100 # (20520 / 300000) * 100 = 6.84
    assert cap_rate == pytest.approx(6.84)

def test_calculate_dscr():
    dscr = calculate_dscr(EXPECTED_NOI, ANNUAL_DEBT_SERVICE)
    expected_dscr = EXPECTED_NOI / ANNUAL_DEBT_SERVICE # 20520 / 17267.04 = 1.188
    assert dscr == pytest.approx(1.188, abs=0.001)

def test_calculate_cash_on_cash():
    coc = calculate_cash_on_cash(EXPECTED_NOI, ANNUAL_DEBT_SERVICE, EXPECTED_TOTAL_CASH)
    cash_flow = EXPECTED_NOI - ANNUAL_DEBT_SERVICE # 20520 - 17267.04 = 3252.96
    expected_coc = (cash_flow / EXPECTED_TOTAL_CASH) * 100 # (3252.96 / 94000) * 100 = 3.46
    assert coc == pytest.approx(3.46, abs=0.001)

def test_handle_division_by_zero():
    """Ensure calculations handle zero denominators gracefully."""
    assert calculate_cap_rate(10000, 0) == 0
    assert calculate_dscr(10000, 0) == 0
    assert calculate_cash_on_cash(10000, 5000, 0) == 0