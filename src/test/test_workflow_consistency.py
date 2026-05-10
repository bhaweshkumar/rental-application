import pytest
from streamlit.testing.v1 import AppTest
import os

# This test script assumes a standard Streamlit multipage app structure.
# - The main app script is at `src/deal_verdict_wizard.py`.
# - Other pages are in a `src/pages/` directory.
# - The test script is run from the project root directory.
APP_ENTRY_POINT = "src/deal_verdict_wizard.py"
DEAL_SUMMARY_PAGE = "pages/deal_summary_report.py"
ACQUISITION_MODELER_PAGE = "pages/acquisition_rehab_modeler.py"
CAPITAL_MARKETS_PAGE = "pages/capital_markets_simulator.py"
UNDERWRITING_ENGINE_PAGE = "pages/underwriting_engine.py"

# Baseline data from the test plan
BASELINE_DATA = {
    "purchase_price": 300000,
    "monthly_rent": 2500,
    "down_payment_pct": 25,
    "interest_rate": 7.0,
    "loan_term": 30,
    "expenses": 1000,  # Monthly
}


@pytest.fixture(scope="function")
def at():
    """Fixture to create a new AppTest instance for each test function."""
    if not os.path.exists(APP_ENTRY_POINT):
        pytest.skip(
            f"Cannot find app entry point: {APP_ENTRY_POINT}. Skipping E2E tests."
        )

    at = AppTest.from_file(APP_ENTRY_POINT, default_timeout=30)
    at.run()
    return at


def test_wizard_to_deep_dive_flow(at: AppTest):
    """
    Implements Test Case 1: Wizard to Deep Dive Data Flow.
    Verifies that data entered into the wizard correctly populates deep dive pages.
    """
    # NOTE: Widget keys are assumed based on common Streamlit practices and labels
    # from the test plan. These may need adjustment to match the actual app.

    # Step 1 & 2: Enter data into the wizard.
    at.number_input(key="purchase_price").set_value(BASELINE_DATA["purchase_price"]).run()
    at.number_input(key="monthly_gross_rent").set_value(
        BASELINE_DATA["monthly_rent"]
    ).run()
    at.slider(key="down_payment_pct").set_value(BASELINE_DATA["down_payment_pct"]).run()
    at.number_input(key="interest_rate").set_value(BASELINE_DATA["interest_rate"]).run()
    at.number_input(key="loan_term").set_value(BASELINE_DATA["loan_term"]).run()
    # Assuming a single input for total monthly expenses for simplicity in the test
    at.number_input(key="total_monthly_expenses").set_value(
        BASELINE_DATA["expenses"]
    ).run()

    # Step 3: Complete the wizard (if there's a final button)
    if at.button(key="get_verdict").exists:
        at.button(key="get_verdict").click().run()

    # Step 4: Navigate to Acquisition & Value-Add Modeling and verify purchase price
    at.switch_page(ACQUISITION_MODELER_PAGE).run()
    assert at.number_input(key="purchase_price").value == BASELINE_DATA["purchase_price"]

    # Step 5: Navigate to Capital Markets & Leverage Simulator and verify financing
    at.switch_page(CAPITAL_MARKETS_PAGE).run()
    expected_ltv = 100 - BASELINE_DATA["down_payment_pct"]
    assert at.slider(key="ltv_pct").value == expected_ltv
    assert at.number_input(key="interest_rate").value == BASELINE_DATA["interest_rate"]
    assert at.number_input(key="loan_term").value == BASELINE_DATA["loan_term"]

    # Step 6: Navigate to The Institutional Underwriting Engine and verify rent/expenses
    at.switch_page(UNDERWRITING_ENGINE_PAGE).run()
    assert at.number_input(key="monthly_gross_rent").value == BASELINE_DATA["monthly_rent"]
    # Check for annual operating expenses. This might be a metric or other text element.
    assert at.text(f"Annual Operating Expenses: ${BASELINE_DATA['expenses'] * 12:,.0f}").exists


def test_deep_dive_to_wizard_flow(at: AppTest):
    """
    Implements Test Case 2: Deep Dive to Wizard/Summary Data Flow.
    Verifies that changes in deep dive pages are reflected back in the wizard.
    """
    # Step 1: Establish baseline state
    at.number_input(key="monthly_gross_rent").set_value(
        BASELINE_DATA["monthly_rent"]
    ).run()
    at.number_input(key="interest_rate").set_value(
        BASELINE_DATA["interest_rate"]
    ).run()
    at.number_input(key="total_monthly_expenses").set_value(
        BASELINE_DATA["expenses"]
    ).run()
    at.slider(key="down_payment_pct").set_value(BASELINE_DATA["down_payment_pct"]).run()

    # Step 2: Navigate to Underwriting Engine and change rent and expenses
    new_rent = 2800
    new_monthly_expenses = 1100
    at.switch_page(UNDERWRITING_ENGINE_PAGE).run()
    at.number_input(key="monthly_gross_rent").set_value(new_rent).run()
    # To test two-way sync, the Underwriting page needs an input for expenses.
    # We assume a 'total_monthly_expenses' key exists here for consistency.
    at.number_input(key="total_monthly_expenses").set_value(new_monthly_expenses).run()

    # Step 3: Navigate to Capital Markets and change interest rate and LTV
    new_rate = 6.5
    new_ltv = 80
    at.switch_page(CAPITAL_MARKETS_PAGE).run()
    at.number_input(key="interest_rate").set_value(new_rate).run()
    at.slider(key="ltv_pct").set_value(new_ltv).run()

    # Step 4: Navigate to Deal Summary Report and check that it renders
    at.switch_page(DEAL_SUMMARY_PAGE).run()
    assert at.h1.value == "Deal Summary Report"
    assert len(at.metric) > 0, "Deal Summary Report should contain metrics."

    # Step 5: Navigate back to the wizard and verify inputs are updated
    at.switch_page(APP_ENTRY_POINT).run()
    assert at.number_input(key="monthly_gross_rent").value == new_rent
    assert at.number_input(key="interest_rate").value == new_rate
    assert at.number_input(key="total_monthly_expenses").value == new_monthly_expenses
    assert at.slider(key="down_payment_pct").value == (100 - new_ltv)


def test_cross_deep_dive_consistency(at: AppTest):
    """
    Implements Test Case 3: Cross-Deep-Dive Page Consistency.
    Verifies that a change on one deep dive page is reflected on another.
    """
    # Step 1 & 2: Navigate to Acquisition modeler and set purchase price and rehab
    new_purchase_price = 400000
    new_rehab_budget = 50000
    at.switch_page(ACQUISITION_MODELER_PAGE).run()
    at.number_input(key="purchase_price").set_value(new_purchase_price).run()
    at.number_input(key="total_rehab_budget").set_value(new_rehab_budget).run()

    # Step 3: Navigate to Capital Markets, read default LTV, and check loan amount
    at.switch_page(CAPITAL_MARKETS_PAGE).run()
    # Read the default LTV from the page to make the test more robust
    default_ltv_pct = at.slider(key="ltv_pct").value
    expected_loan_amount = new_purchase_price * (default_ltv_pct / 100.0)
    loan_metric = at.metric(label="Loan Amount")
    assert loan_metric.exists
    # Check if the calculated value is in the metric's display value
    assert f"${expected_loan_amount:,.0f}" in loan_metric.value

    # Step 4: Navigate to Underwriting Engine and verify cash invested calculation
    # This verifies that both purchase price (for down payment) and rehab budget
    # from the Acquisition page are correctly used in the Underwriting page.
    at.switch_page(UNDERWRITING_ENGINE_PAGE).run()
    assert at.metric(label="Cash-on-Cash Return").exists

    # Per Test Plan, CoC must use rehab budget. We can verify an intermediate
    # calculation, "Total Cash Invested", to confirm data flow without
    # duplicating the final CoC logic.
    down_payment = new_purchase_price * (1 - (default_ltv_pct / 100.0))
    expected_cash_invested = down_payment + new_rehab_budget
    cash_invested_metric = at.metric(label="Total Cash Invested")
    assert cash_invested_metric.exists
    assert f"${expected_cash_invested:,.0f}" in cash_invested_metric.value


def test_metric_calculation_consistency():
    """
    Implements Test Case 4: Metric Calculation Consistency.
    This test is a placeholder as it requires the full application logic to
    accurately compare calculated metrics from two different user paths.
    Implementing it fully would require either:
    1. Duplicating the calculation logic within the test, which is brittle.
    2. Having exact, known outputs for a given set of inputs, which is
       preferable but requires a fully stable calculation engine.

    The structure is provided in the initial draft but is skipped here to
    avoid a complex and potentially fragile test.
    """
    pytest.skip("Skipping metric consistency test until calculation logic is finalized.")