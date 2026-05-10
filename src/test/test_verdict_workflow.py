import pytest

from src.logic.financing import calculate_loan_details, calculate_monthly_payment
from src.logic.models import (
    CapitalMarketsDetails,
    DealProfile,
    ExpenseLineItems,
    PropertyDetails,
    VerdictInputs,
)
from src.logic.verdict import (
    apply_verdict_to_underwriting_fields,
    calculate_annual_operating_expenses,
    classify_verdict,
    evaluate_deal_verdict,
    get_missing_fields_for_step,
    refresh_deal_calculations,
)


def _build_capital_details(purchase_price: float, ltv_pct: int, rate_pct: float, term_years: int, closing_costs_pct: int) -> CapitalMarketsDetails:
    loan_amount, down_payment, closing_costs = calculate_loan_details(
        purchase_price, ltv_pct, closing_costs_pct
    )
    monthly_payment = calculate_monthly_payment(loan_amount, rate_pct, term_years)
    return CapitalMarketsDetails(
        loan_type="DSCR",
        ltv_pct=ltv_pct,
        interest_rate_pct=rate_pct,
        term_years=term_years,
        closing_costs_pct=closing_costs_pct,
        loan_amount=loan_amount,
        down_payment=down_payment,
        closing_costs=closing_costs,
        monthly_payment=monthly_payment,
        annual_debt_service=monthly_payment * 12,
    )


def test_calculate_annual_operating_expenses_from_line_items():
    expenses = ExpenseLineItems(
        annual_property_taxes=3600,
        annual_insurance=1200,
        monthly_hoa=75,
        monthly_property_management=150,
        monthly_maintenance_reserve=125,
        monthly_owner_paid_utilities=100,
        monthly_other_expenses=50,
    )

    total = calculate_annual_operating_expenses(expenses)

    assert total == pytest.approx(10800)


@pytest.mark.parametrize(
    "monthly_cash_flow, dscr, expected_status",
    [
        (300, 1.20, "Pass"),
        (299.99, 1.25, "Caution"),
        (100, 1.19, "Caution"),
        (-1, 1.30, "Fail"),
        (500, 0.99, "Fail"),
    ],
)
def test_classify_verdict_status_thresholds(monthly_cash_flow, dscr, expected_status):
    status, reasons = classify_verdict(monthly_cash_flow=monthly_cash_flow, dscr=dscr)

    assert status == expected_status
    assert reasons


@pytest.mark.parametrize(
    "monthly_rent, expected_status",
    [
        (2500, "Pass"),
        (2400, "Caution"),
        (2000, "Fail"),
    ],
)
def test_evaluate_deal_verdict_status_thresholds(monthly_rent, expected_status):
    purchase_price = 250000
    deal = DealProfile(
        property_details=PropertyDetails(
            address="123 Main St",
            asset_type="Single-Family",
            sq_ft=1400,
            year_built=1998,
            state="Texas",
        ),
        capital_markets_details=_build_capital_details(
            purchase_price=purchase_price,
            ltv_pct=75,
            rate_pct=7.5,
            term_years=30,
            closing_costs_pct=3,
        ),
        verdict_inputs=VerdictInputs(
            monthly_rent=monthly_rent,
            monthly_other_income=0,
            vacancy_pct=5,
            rent_ready_repairs=5000,
        ),
        expense_line_items=ExpenseLineItems(
            annual_property_taxes=3600,
            annual_insurance=1200,
            monthly_hoa=0,
            monthly_property_management=150,
            monthly_maintenance_reserve=125,
            monthly_owner_paid_utilities=75,
            monthly_other_expenses=0,
        ),
    )
    deal.acquisition_details.purchase_price = purchase_price

    outputs = evaluate_deal_verdict(deal)

    assert outputs.verdict_status == expected_status
    assert outputs.verdict_reasons


def test_evaluate_deal_verdict_computes_monthly_cash_flow_and_total_cash_required():
    purchase_price = 250000
    deal = DealProfile(
        property_details=PropertyDetails(address="123 Main St", state="Texas"),
        capital_markets_details=_build_capital_details(
            purchase_price=purchase_price,
            ltv_pct=75,
            rate_pct=7.5,
            term_years=30,
            closing_costs_pct=3,
        ),
        verdict_inputs=VerdictInputs(
            monthly_rent=2500,
            monthly_other_income=100,
            vacancy_pct=5,
            rent_ready_repairs=5000,
        ),
        expense_line_items=ExpenseLineItems(
            annual_property_taxes=3600,
            annual_insurance=1200,
            monthly_hoa=0,
            monthly_property_management=150,
            monthly_maintenance_reserve=125,
            monthly_owner_paid_utilities=75,
            monthly_other_expenses=0,
        ),
    )
    deal.acquisition_details.purchase_price = purchase_price

    outputs = evaluate_deal_verdict(deal)

    assert outputs.monthly_cash_flow == pytest.approx(408.97, abs=0.01)
    assert outputs.total_cash_required == pytest.approx(75000, abs=0.01)
    assert outputs.dscr == pytest.approx(1.31, abs=0.01)
    assert outputs.cap_rate == pytest.approx(8.26, abs=0.01)
    assert outputs.cash_on_cash_return == pytest.approx(6.54, abs=0.01)


def test_get_missing_fields_for_step_blocks_progression_until_required_inputs_present():
    deal = DealProfile()

    assert "address" in get_missing_fields_for_step("property", deal)

    deal.property_details.address = "123 Main St"
    deal.property_details.state = "Texas"
    deal.property_details.sq_ft = 1200
    deal.property_details.year_built = 1990
    deal.acquisition_details.purchase_price = 200000

    assert get_missing_fields_for_step("property", deal) == []
    assert "monthly_rent" in get_missing_fields_for_step("rent", deal)

    deal.verdict_inputs.monthly_rent = 2500
    assert "loan_amount" in get_missing_fields_for_step("financing", deal)

    deal.capital_markets_details.loan_amount = 150000
    deal.capital_markets_details.monthly_payment = 1200
    deal.capital_markets_details.annual_debt_service = 14400
    assert "annual_property_taxes" in get_missing_fields_for_step("expenses", deal)


@pytest.mark.parametrize("asset_type", ["Condo", "Townhome"])
def test_get_missing_fields_for_step_requires_hoa_for_condo_and_townhome(asset_type):
    deal = DealProfile()
    deal.property_details.asset_type = asset_type
    deal.expense_line_items.annual_property_taxes = 3000
    deal.expense_line_items.annual_insurance = 1200
    deal.expense_line_items.monthly_property_management = 150
    deal.expense_line_items.monthly_maintenance_reserve = 125

    missing = get_missing_fields_for_step("expenses", deal)

    assert "monthly_hoa" in missing


def test_get_missing_fields_for_step_does_not_require_hoa_for_single_family():
    deal = DealProfile()
    deal.property_details.asset_type = "Single-Family"
    deal.expense_line_items.annual_property_taxes = 3000
    deal.expense_line_items.annual_insurance = 1200
    deal.expense_line_items.monthly_property_management = 150
    deal.expense_line_items.monthly_maintenance_reserve = 125

    missing = get_missing_fields_for_step("expenses", deal)

    assert "monthly_hoa" not in missing


def test_evaluate_deal_verdict_counts_hoa_in_profitability():
    purchase_price = 250000
    deal = DealProfile(
        property_details=PropertyDetails(
            address="123 Main St",
            asset_type="Condo",
            state="Texas",
            sq_ft=1100,
            year_built=2001,
        ),
        capital_markets_details=_build_capital_details(
            purchase_price=purchase_price,
            ltv_pct=75,
            rate_pct=7.5,
            term_years=30,
            closing_costs_pct=3,
        ),
        verdict_inputs=VerdictInputs(
            monthly_rent=2500,
            monthly_other_income=0,
            vacancy_pct=5,
            rent_ready_repairs=5000,
        ),
        expense_line_items=ExpenseLineItems(
            annual_property_taxes=3600,
            annual_insurance=1200,
            monthly_hoa=250,
            monthly_property_management=150,
            monthly_maintenance_reserve=125,
            monthly_owner_paid_utilities=75,
            monthly_other_expenses=0,
        ),
    )
    deal.acquisition_details.purchase_price = purchase_price

    outputs = evaluate_deal_verdict(deal)

    assert outputs.annual_operating_expenses == pytest.approx(12000, abs=0.01)
    assert outputs.monthly_cash_flow == pytest.approx(63.97, abs=0.01)


def test_apply_verdict_to_underwriting_fields_keeps_legacy_pages_in_sync():
    purchase_price = 250000
    deal = DealProfile(
        property_details=PropertyDetails(address="123 Main St", state="Texas"),
        capital_markets_details=_build_capital_details(
            purchase_price=purchase_price,
            ltv_pct=75,
            rate_pct=7.5,
            term_years=30,
            closing_costs_pct=3,
        ),
        verdict_inputs=VerdictInputs(
            monthly_rent=2500,
            monthly_other_income=100,
            vacancy_pct=5,
            rent_ready_repairs=5000,
        ),
        expense_line_items=ExpenseLineItems(
            annual_property_taxes=3600,
            annual_insurance=1200,
            monthly_hoa=0,
            monthly_property_management=150,
            monthly_maintenance_reserve=125,
            monthly_owner_paid_utilities=75,
            monthly_other_expenses=0,
        ),
    )
    deal.acquisition_details.purchase_price = purchase_price
    deal.verdict_outputs = evaluate_deal_verdict(deal)

    apply_verdict_to_underwriting_fields(deal)

    assert deal.underwriting_inputs.monthly_gross_rent == pytest.approx(2600)
    assert deal.underwriting_inputs.vacancy_pct == 5
    assert deal.underwriting_inputs.opex_pct == pytest.approx(30.36, abs=0.01)
    assert deal.underwriting_outputs.noi == pytest.approx(deal.verdict_outputs.noi)
    assert deal.underwriting_outputs.dscr == pytest.approx(deal.verdict_outputs.dscr)
    assert deal.underwriting_outputs.cap_rate_purchase == pytest.approx(deal.verdict_outputs.cap_rate)
    assert deal.underwriting_outputs.cash_on_cash_return == pytest.approx(
        deal.verdict_outputs.cash_on_cash_return
    )


def test_refresh_deal_calculations_recomputes_financing_verdict_and_underwriting():
    deal = DealProfile(
        property_details=PropertyDetails(
            address="123 Main St",
            asset_type="Single-Family",
            sq_ft=1400,
            year_built=1998,
            state="Texas",
        ),
        verdict_inputs=VerdictInputs(
            monthly_rent=2500,
            monthly_other_income=100,
            vacancy_pct=5,
            rent_ready_repairs=5000,
        ),
        expense_line_items=ExpenseLineItems(
            annual_property_taxes=3600,
            annual_insurance=1200,
            monthly_hoa=0,
            monthly_property_management=150,
            monthly_maintenance_reserve=125,
            monthly_owner_paid_utilities=75,
            monthly_other_expenses=0,
        ),
    )
    deal.acquisition_details.purchase_price = 250000
    deal.capital_markets_details.loan_type = "DSCR"
    deal.capital_markets_details.ltv_pct = 75
    deal.capital_markets_details.interest_rate_pct = 7.5
    deal.capital_markets_details.term_years = 30
    deal.capital_markets_details.closing_costs_pct = 3
    deal.other_details["wizard_financing_mode"] = "LTV %"

    refresh_deal_calculations(deal)

    assert deal.capital_markets_details.loan_amount == pytest.approx(187500.0)
    assert deal.capital_markets_details.down_payment == pytest.approx(62500.0)
    assert deal.capital_markets_details.closing_costs == pytest.approx(7500.0)
    assert deal.capital_markets_details.monthly_payment == pytest.approx(1311.03, abs=0.01)
    assert deal.verdict_outputs.verdict_status == "Pass"
    assert deal.verdict_outputs.monthly_cash_flow == pytest.approx(408.97, abs=0.01)
    assert deal.underwriting_outputs.noi == pytest.approx(deal.verdict_outputs.noi)
    assert deal.underwriting_outputs.dscr == pytest.approx(deal.verdict_outputs.dscr)
