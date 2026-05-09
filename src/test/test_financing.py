import pytest
from src.logic.financing import calculate_loan_details, calculate_monthly_payment

def test_calculate_loan_details():
    """Tests the calculation of loan amount, down payment, and closing costs."""
    purchase_price = 300000
    ltv_pct = 80
    closing_costs_pct = 3

    loan_amount, down_payment, closing_costs = calculate_loan_details(
        purchase_price, ltv_pct, closing_costs_pct
    )

    assert loan_amount == 240000
    assert down_payment == 60000
    assert closing_costs == 9000 # 3% of purchase price

@pytest.mark.parametrize(
    "loan_amount, annual_rate_pct, term_years, expected_payment",
    [
        (240000, 6.0, 30, 1438.92), # Standard 30-year mortgage
        (500000, 7.5, 30, 3496.07),
        (240000, 6.0, 15, 2025.26), # 15-year mortgage
        (0, 5.0, 30, 0), # Zero loan amount
    ]
)
def test_calculate_monthly_payment(loan_amount, annual_rate_pct, term_years, expected_payment):
    """Tests the monthly mortgage payment calculation."""
    monthly_payment = calculate_monthly_payment(loan_amount, annual_rate_pct, term_years)
    assert monthly_payment == pytest.approx(expected_payment, abs=0.01)

def test_calculate_monthly_payment_zero_interest():
    """Tests monthly payment with zero interest."""
    monthly_payment = calculate_monthly_payment(loan_amount=360000, annual_rate_pct=0, term_years=30)
    assert monthly_payment == pytest.approx(1000)
