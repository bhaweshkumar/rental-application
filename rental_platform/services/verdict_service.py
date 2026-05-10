"""Verdict evaluation service — deal scoring and calculation refresh."""
from typing import List, Tuple

from rental_platform.models import (
    DealProfile,
    ExpenseLineItems,
    UnderwritingInputs,
    UnderwritingOutputs,
    VerdictOutputs,
)
from rental_platform.services.financing_service import (
    calculate_loan_details,
    calculate_monthly_payment,
)
from rental_platform.services.underwriting_service import (
    calculate_cap_rate,
    calculate_cash_on_cash,
    calculate_dscr,
    calculate_noi,
    calculate_total_cash_invested,
)


def calculate_annual_operating_expenses(expenses: ExpenseLineItems) -> float:
    """Converts line-item operating costs into a single annual expense figure."""
    monthly_total = (
        expenses.monthly_hoa
        + expenses.monthly_property_management
        + expenses.monthly_maintenance_reserve
        + expenses.monthly_owner_paid_utilities
        + expenses.monthly_other_expenses
    )
    return expenses.annual_property_taxes + expenses.annual_insurance + (monthly_total * 12)


def classify_verdict(
    monthly_cash_flow: float, dscr: float, *, has_missing_inputs: bool = False
) -> Tuple[str, List[str]]:
    """Classifies a deal according to the cash-flow-first passive rental rules."""
    reasons: List[str] = []

    if has_missing_inputs:
        return "Fail", ["Required inputs are missing for a complete verdict."]

    if monthly_cash_flow < 0:
        reasons.append("Monthly cash flow is negative after debt service.")
    if dscr < 1.0:
        reasons.append("DSCR is below 1.00, which indicates the property does not cover debt safely.")
    if reasons:
        return "Fail", reasons

    if monthly_cash_flow >= 300 and dscr >= 1.20:
        return "Pass", [
            "Monthly cash flow meets or exceeds the $300 passive-income target.",
            "DSCR meets or exceeds the 1.20 lender safety threshold.",
        ]

    if monthly_cash_flow < 300:
        reasons.append("Monthly cash flow is positive but below the $300 target.")
    if 1.0 <= dscr < 1.20:
        reasons.append("DSCR is positive but below the 1.20 comfort threshold.")

    return "Caution", reasons or ["The deal is workable, but it does not clear the preferred passive-income buffer."]


def get_missing_fields_for_step(step: str, deal: DealProfile) -> List[str]:
    """Returns the required fields still missing for a wizard step."""
    missing: List[str] = []

    if step == "property":
        if not deal.property_details.address.strip():
            missing.append("address")
        if not deal.property_details.state:
            missing.append("state")
        if deal.property_details.sq_ft <= 0:
            missing.append("sq_ft")
        if deal.property_details.year_built <= 0:
            missing.append("year_built")
        if deal.acquisition_details.purchase_price <= 0:
            missing.append("purchase_price")
        return missing

    if step == "rent":
        if deal.verdict_inputs.monthly_rent <= 0:
            missing.append("monthly_rent")
        return missing

    if step == "financing":
        if deal.capital_markets_details.loan_amount <= 0:
            missing.append("loan_amount")
        if deal.capital_markets_details.monthly_payment <= 0:
            missing.append("monthly_payment")
        if deal.capital_markets_details.annual_debt_service <= 0:
            missing.append("annual_debt_service")
        return missing

    if step == "expenses":
        if deal.expense_line_items.annual_property_taxes <= 0:
            missing.append("annual_property_taxes")
        if deal.expense_line_items.annual_insurance <= 0:
            missing.append("annual_insurance")
        if (
            deal.property_details.asset_type in {"Condo", "Townhome"}
            and deal.expense_line_items.monthly_hoa <= 0
        ):
            missing.append("monthly_hoa")
        if deal.expense_line_items.monthly_property_management <= 0:
            missing.append("monthly_property_management")
        if deal.expense_line_items.monthly_maintenance_reserve <= 0:
            missing.append("monthly_maintenance_reserve")
        return missing

    return missing


def evaluate_deal_verdict(deal: DealProfile) -> VerdictOutputs:
    """Computes the verdict metrics for the guided rental workflow."""
    verdict_inputs = deal.verdict_inputs
    expenses = deal.expense_line_items
    capital = deal.capital_markets_details
    purchase_price = deal.acquisition_details.purchase_price

    annual_gross_rent = (verdict_inputs.monthly_rent + verdict_inputs.monthly_other_income) * 12
    annual_operating_expenses = calculate_annual_operating_expenses(expenses)
    effective_gross_income = annual_gross_rent * (1 - (verdict_inputs.vacancy_pct / 100.0))
    noi = calculate_noi(annual_gross_rent, verdict_inputs.vacancy_pct, annual_operating_expenses)
    total_cash_required = calculate_total_cash_invested(
        capital.down_payment,
        capital.closing_costs,
        verdict_inputs.rent_ready_repairs,
    )
    dscr = calculate_dscr(noi, capital.annual_debt_service)
    monthly_cash_flow = (noi - capital.annual_debt_service) / 12 if capital.annual_debt_service else 0.0
    cap_rate = calculate_cap_rate(noi, purchase_price)
    cash_on_cash_return = calculate_cash_on_cash(noi, capital.annual_debt_service, total_cash_required)

    has_missing_inputs = bool(
        get_missing_fields_for_step("property", deal)
        or get_missing_fields_for_step("rent", deal)
        or get_missing_fields_for_step("financing", deal)
        or get_missing_fields_for_step("expenses", deal)
    )
    verdict_status, verdict_reasons = classify_verdict(
        monthly_cash_flow=monthly_cash_flow,
        dscr=dscr,
        has_missing_inputs=has_missing_inputs,
    )

    return VerdictOutputs(
        annual_operating_expenses=annual_operating_expenses,
        effective_gross_income=effective_gross_income,
        noi=noi,
        monthly_cash_flow=monthly_cash_flow,
        dscr=dscr,
        cap_rate=cap_rate,
        cash_on_cash_return=cash_on_cash_return,
        total_cash_required=total_cash_required,
        verdict_status=verdict_status,
        verdict_reasons=verdict_reasons,
    )


def refresh_deal_calculations(deal: DealProfile) -> None:
    """Keeps shared financing, verdict, and underwriting outputs in sync."""
    capital = deal.capital_markets_details
    purchase_price = float(deal.acquisition_details.purchase_price)
    financing_mode = deal.other_details.get("wizard_financing_mode", "LTV %")

    if purchase_price <= 0:
        capital.loan_amount = 0.0
        capital.closing_costs = 0.0
        capital.monthly_payment = 0.0
        capital.annual_debt_service = 0.0
    else:
        if financing_mode == "Down Payment $":
            down_payment = max(min(float(capital.down_payment), purchase_price), 0.0)
            loan_amount = max(purchase_price - down_payment, 0.0)
            capital.ltv_pct = int(round((loan_amount / purchase_price) * 100)) if purchase_price else capital.ltv_pct
            closing_costs = purchase_price * (capital.closing_costs_pct / 100.0)
        else:
            loan_amount, down_payment, closing_costs = calculate_loan_details(
                purchase_price,
                capital.ltv_pct,
                capital.closing_costs_pct,
            )

        monthly_payment = calculate_monthly_payment(
            loan_amount,
            capital.interest_rate_pct,
            capital.term_years,
        )

        capital.loan_amount = loan_amount
        capital.down_payment = down_payment
        capital.closing_costs = closing_costs
        capital.monthly_payment = monthly_payment
        capital.annual_debt_service = monthly_payment * 12

    deal.verdict_outputs = evaluate_deal_verdict(deal)
    apply_verdict_to_underwriting_fields(deal)


def apply_verdict_to_underwriting_fields(deal: DealProfile) -> None:
    """Backfills the legacy underwriting models from the verdict workflow data."""
    verdict_inputs = deal.verdict_inputs
    verdict_outputs = deal.verdict_outputs
    annual_gross_rent = (verdict_inputs.monthly_rent + verdict_inputs.monthly_other_income) * 12
    egi = annual_gross_rent * (1 - (verdict_inputs.vacancy_pct / 100.0))
    opex_pct = (
        (verdict_outputs.annual_operating_expenses / egi) * 100.0
        if egi > 0
        else 0.0
    )

    deal.underwriting_inputs = UnderwritingInputs(
        monthly_gross_rent=verdict_inputs.monthly_rent + verdict_inputs.monthly_other_income,
        vacancy_pct=verdict_inputs.vacancy_pct,
        opex_pct=opex_pct,
    )
    deal.underwriting_outputs = UnderwritingOutputs(
        noi=verdict_outputs.noi,
        cap_rate_purchase=verdict_outputs.cap_rate,
        dscr=verdict_outputs.dscr,
        cash_on_cash_return=verdict_outputs.cash_on_cash_return,
        total_cash_invested=verdict_outputs.total_cash_required,
    )
