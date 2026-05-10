"""Loan and financing calculation service."""
from typing import Optional, Tuple


def calculate_loan_details(
    purchase_price: float, ltv_pct: int, closing_costs_pct: int
) -> Tuple[float, float, float]:
    """Calculates loan amount, down payment, and closing costs."""
    loan_amount = purchase_price * (ltv_pct / 100.0)
    down_payment = purchase_price - loan_amount
    closing_costs = purchase_price * (closing_costs_pct / 100.0)
    return loan_amount, down_payment, closing_costs


def calculate_monthly_payment(
    loan_amount: float,
    annual_rate_pct: float = 0.0,
    term_years: int = 0,
    *,
    annual_interest_rate_pct: Optional[float] = None,
) -> float:
    """Calculates the monthly principal and interest payment for a loan."""
    if loan_amount <= 0:
        return 0.0

    if annual_interest_rate_pct is not None:
        annual_rate_pct = annual_interest_rate_pct

    if annual_rate_pct == 0:
        return loan_amount / (term_years * 12) if term_years > 0 else loan_amount

    monthly_rate = (annual_rate_pct / 100.0) / 12
    num_payments = term_years * 12

    if num_payments == 0:
        return loan_amount

    monthly_payment = loan_amount * (
        (monthly_rate * (1 + monthly_rate) ** num_payments)
        / ((1 + monthly_rate) ** num_payments - 1)
    )
    return monthly_payment
