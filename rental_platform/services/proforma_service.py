"""Proforma projection service."""
from typing import List

from rental_platform.models import ProformaAssumptions, ProformaYear


def generate_proforma(
    initial_gross_rent: float,
    initial_opex: float,
    vacancy_pct: int,
    annual_debt_service: float,
    assumptions: ProformaAssumptions,
) -> List[ProformaYear]:
    """Generates a multi-year proforma based on growth assumptions."""
    proforma_years = []
    current_gpr = initial_gross_rent
    current_opex = initial_opex

    for year in range(1, assumptions.holding_period_years + 1):
        if year > 1:
            current_gpr *= (1 + assumptions.rent_growth_pct / 100.0)
            current_opex *= (1 + assumptions.expense_growth_pct / 100.0)

        vacancy_loss = current_gpr * (vacancy_pct / 100.0)
        egi = current_gpr - vacancy_loss
        noi = egi - current_opex
        cfbt = noi - annual_debt_service

        proforma_years.append(
            ProformaYear(
                year=year,
                gross_potential_rent=current_gpr,
                vacancy_loss=vacancy_loss,
                effective_gross_income=egi,
                operating_expenses=current_opex,
                noi=noi,
                debt_service=annual_debt_service,
                cash_flow_before_tax=cfbt,
            )
        )

    return proforma_years
