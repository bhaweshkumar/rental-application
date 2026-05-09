try:
    from src.shared.models import ProfitFirstInputs, ProfitFirstOutputs  # type: ignore
except ImportError:
    from shared.models import ProfitFirstInputs, ProfitFirstOutputs  # type: ignore

def calculate_profit_first_allocations(
    gross_income: float,
    taps: ProfitFirstInputs,
) -> ProfitFirstOutputs:
    """Calculates cash sweeps based on Target Allocation Percentages (TAPs)."""
    profit_allocation = gross_income * (taps.profit_tap_pct / 100.0)
    owners_pay_allocation = gross_income * (taps.owners_pay_tap_pct / 100.0)
    tax_allocation = gross_income * (taps.tax_tap_pct / 100.0)

    total_allocations = profit_allocation + owners_pay_allocation + tax_allocation
    opex_allocation = gross_income - total_allocations

    return ProfitFirstOutputs(
        profit_allocation=profit_allocation,
        owners_pay_allocation=owners_pay_allocation,
        tax_allocation=tax_allocation,
        opex_allocation=opex_allocation,
    )
