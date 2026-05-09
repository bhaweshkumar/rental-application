def calculate_total_cash_invested(
    down_payment: float, closing_costs: float, rehab_budget: float
) -> float:
    """Calculates the total cash required to close a deal."""
    return down_payment + closing_costs + rehab_budget

def calculate_noi(annual_gross_rent: float, vacancy_pct: int, operating_expenses: float) -> float:
    """Calculates Net Operating Income (NOI)."""
    effective_gross_income = annual_gross_rent * (1 - (vacancy_pct / 100.0))
    noi = effective_gross_income - operating_expenses
    return noi

def calculate_cap_rate(noi: float, purchase_price: float) -> float:
    """Calculates the Capitalization Rate as a percentage."""
    if purchase_price <= 0:
        return 0.0
    return (noi / purchase_price) * 100.0

def calculate_dscr(noi: float, annual_debt_service: float) -> float:
    """Calculates the Debt Service Coverage Ratio."""
    if annual_debt_service <= 0:
        return 0.0
    return noi / annual_debt_service

def calculate_cash_on_cash(noi: float, annual_debt_service: float, total_cash_invested: float) -> float:
    """Calculates the Cash-on-Cash Return as a percentage."""
    if total_cash_invested <= 0:
        return 0.0
    cash_flow_before_tax = noi - annual_debt_service
    return (cash_flow_before_tax / total_cash_invested) * 100.0