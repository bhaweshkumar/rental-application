try:
    from src.shared.models import BrrrrMetrics  # type: ignore
except ImportError:
    from shared.models import BrrrrMetrics  # type: ignore


def calculate_brrrr_metrics(
    purchase_price: float,
    total_rehab_budget: float,
    arv: float,
    refi_ltv_pct: int,
) -> BrrrrMetrics:
    """Calculates key metrics for a BRRRR strategy."""
    all_in_cost = purchase_price + total_rehab_budget
    equity_capture = arv - all_in_cost
    refi_loan_amount = arv * (refi_ltv_pct / 100.0)
    cash_out_proceeds = refi_loan_amount - all_in_cost

    return BrrrrMetrics(
        all_in_cost=all_in_cost,
        equity_capture=equity_capture,
        refi_loan_amount=refi_loan_amount,
        cash_out_proceeds=cash_out_proceeds,
    )
