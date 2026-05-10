import streamlit as st

from logic.financing import calculate_loan_details, calculate_monthly_payment
from logic.verdict import get_missing_fields_for_step
from shared.constants import ASSET_TYPE_OPTIONS, US_STATES
from shared.utils import get_safe_index
from verdict_summary import render_verdict_summary


WIZARD_STEPS = [
    ("property", "Property"),
    ("rent", "Rent"),
    ("financing", "Financing"),
    ("expenses", "Expenses"),
    ("verdict", "Verdict"),
]


def _go_to_next_step() -> None:
    st.session_state.deal_wizard_step = min(
        st.session_state.deal_wizard_step + 1,
        len(WIZARD_STEPS) - 1,
    )


def _go_to_previous_step() -> None:
    st.session_state.deal_wizard_step = max(st.session_state.deal_wizard_step - 1, 0)


def _show_step_header(step_label: str, step_index: int) -> None:
    st.header("Deal Verdict Wizard")
    st.caption(
        "A guided workflow for deciding whether a property is priced well enough to work as a passive long-term rental."
    )
    st.progress((step_index + 1) / len(WIZARD_STEPS))
    labels = " -> ".join(
        f"{idx + 1}. {label}" for idx, (_, label) in enumerate(WIZARD_STEPS)
    )
    st.caption(labels)
    st.subheader(f"Step {step_index + 1}: {step_label}")


def _render_property_step(deal_profile) -> None:
    property_details = deal_profile.property_details
    acquisition_details = deal_profile.acquisition_details

    with st.form("deal_verdict_property_form"):
        address = st.text_input("Property Address", value=property_details.address)
        asset_type = st.selectbox(
            "Asset Type",
            options=ASSET_TYPE_OPTIONS,
            index=get_safe_index(ASSET_TYPE_OPTIONS, property_details.asset_type),
        )
        col1, col2 = st.columns(2)
        with col1:
            sq_ft = st.number_input(
                "Square Footage",
                min_value=0,
                value=int(property_details.sq_ft),
                step=50,
            )
        with col2:
            year_built = st.number_input(
                "Year Built",
                min_value=1800,
                max_value=2100,
                value=int(property_details.year_built),
                step=1,
            )
        state = st.selectbox(
            "State",
            options=US_STATES,
            index=get_safe_index(US_STATES, property_details.state),
        )
        purchase_price = st.number_input(
            "Asking Price",
            min_value=0,
            value=int(acquisition_details.purchase_price),
            step=5000,
        )

        if st.form_submit_button("Save Property & Continue"):
            property_details.address = address
            property_details.asset_type = asset_type
            property_details.sq_ft = sq_ft
            property_details.year_built = year_built
            property_details.state = state
            acquisition_details.purchase_price = purchase_price

            missing = get_missing_fields_for_step("property", deal_profile)
            if missing:
                st.warning(f"Complete the required fields before continuing: {', '.join(missing)}")
            else:
                _go_to_next_step()
                st.rerun()


def _render_rent_step(deal_profile) -> None:
    verdict_inputs = deal_profile.verdict_inputs

    with st.form("deal_verdict_rent_form"):
        monthly_rent = st.number_input(
            "Expected Monthly Rent",
            min_value=0,
            value=float(verdict_inputs.monthly_rent),
            step=100.0,
        )
        monthly_other_income = st.number_input(
            "Other Monthly Income",
            min_value=0,
            value=float(verdict_inputs.monthly_other_income),
            step=25.0,
            help="Parking, pet rent, laundry, or other recurring monthly income.",
        )
        vacancy_pct = st.slider(
            "Vacancy Rate (%)",
            min_value=0,
            max_value=20,
            value=int(verdict_inputs.vacancy_pct),
            step=1,
        )

        if st.form_submit_button("Save Rent & Continue"):
            verdict_inputs.monthly_rent = monthly_rent
            verdict_inputs.monthly_other_income = monthly_other_income
            verdict_inputs.vacancy_pct = vacancy_pct

            missing = get_missing_fields_for_step("rent", deal_profile)
            if missing:
                st.warning(f"Complete the required fields before continuing: {', '.join(missing)}")
            else:
                _go_to_next_step()
                st.rerun()

    if st.button("Back to Property"):
        _go_to_previous_step()
        st.rerun()


def _render_financing_step(deal_profile) -> None:
    capital_details = deal_profile.capital_markets_details
    purchase_price = deal_profile.acquisition_details.purchase_price
    financing_mode = deal_profile.other_details.get("wizard_financing_mode", "LTV %")

    if purchase_price <= 0:
        st.warning("Set the asking price first in Step 1.")
        return

    with st.form("deal_verdict_financing_form"):
        loan_type = st.selectbox(
            "Loan Type",
            options=["DSCR", "Conventional", "FHA", "Creative"],
            index=get_safe_index(["DSCR", "Conventional", "FHA", "Creative"], capital_details.loan_type),
        )
        financing_mode = st.selectbox(
            "Financing Input Mode",
            options=["LTV %", "Down Payment $"],
            index=get_safe_index(["LTV %", "Down Payment $"], financing_mode),
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            if financing_mode == "LTV %":
                ltv_pct = st.slider(
                    "Loan-to-Value (LTV) %",
                    min_value=50,
                    max_value=97,
                    value=int(capital_details.ltv_pct),
                    step=1,
                )
                loan_amount, down_payment, closing_costs = calculate_loan_details(
                    purchase_price,
                    ltv_pct,
                    capital_details.closing_costs_pct,
                )
            else:
                down_payment = st.number_input(
                    "Down Payment ($)",
                    min_value=0.0,
                    max_value=float(purchase_price),
                    value=float(capital_details.down_payment),
                    step=5000.0,
                )
                loan_amount = max(purchase_price - down_payment, 0.0)
                ltv_pct = int(round((loan_amount / purchase_price) * 100)) if purchase_price else 0
                closing_costs = purchase_price * (capital_details.closing_costs_pct / 100.0)
            interest_rate_pct = st.number_input(
                "Interest Rate (%)",
                min_value=0.0,
                max_value=20.0,
                value=float(capital_details.interest_rate_pct),
                step=0.125,
            )
        with col2:
            term_years = st.selectbox(
                "Loan Term (Years)",
                options=[30, 25, 20, 15],
                index=get_safe_index([30, 25, 20, 15], capital_details.term_years),
            )
            closing_costs_pct = st.slider(
                "Closing Costs (%)",
                min_value=0,
                max_value=7,
                value=int(capital_details.closing_costs_pct),
                step=1,
            )
        with col3:
            st.metric("Loan Amount", f"${loan_amount:,.0f}")
            st.metric("Down Payment", f"${down_payment:,.0f}")
            st.metric("Implied LTV", f"{ltv_pct}%")

        if financing_mode == "LTV %":
            loan_amount, down_payment, closing_costs = calculate_loan_details(
                purchase_price,
                ltv_pct,
                closing_costs_pct,
            )
        else:
            closing_costs = purchase_price * (closing_costs_pct / 100.0)

        monthly_payment = calculate_monthly_payment(loan_amount, interest_rate_pct, term_years)
        annual_debt_service = monthly_payment * 12

        st.info(
            f"Estimated monthly principal and interest: ${monthly_payment:,.0f}. "
            f"Estimated cash to close before rent-ready repairs: ${down_payment + closing_costs:,.0f}."
        )

        if st.form_submit_button("Save Financing & Continue"):
            deal_profile.other_details["wizard_financing_mode"] = financing_mode
            capital_details.loan_type = loan_type
            capital_details.ltv_pct = ltv_pct
            capital_details.interest_rate_pct = interest_rate_pct
            capital_details.term_years = term_years
            capital_details.closing_costs_pct = closing_costs_pct
            capital_details.loan_amount = loan_amount
            capital_details.down_payment = down_payment
            capital_details.closing_costs = closing_costs
            capital_details.monthly_payment = monthly_payment
            capital_details.annual_debt_service = annual_debt_service

            missing = get_missing_fields_for_step("financing", deal_profile)
            if missing:
                st.warning(f"Complete the required fields before continuing: {', '.join(missing)}")
            else:
                _go_to_next_step()
                st.rerun()

    if st.button("Back to Rent"):
        _go_to_previous_step()
        st.rerun()


def _render_expenses_step(deal_profile) -> None:
    expenses = deal_profile.expense_line_items
    verdict_inputs = deal_profile.verdict_inputs

    with st.form("deal_verdict_expenses_form"):
        st.markdown("Enter the recurring costs that matter for passive rental cash flow.")
        col1, col2 = st.columns(2)
        with col1:
            annual_property_taxes = st.number_input(
                "Annual Property Taxes",
                min_value=0.0,
                value=float(expenses.annual_property_taxes),
                step=250.0,
            )
            annual_insurance = st.number_input(
                "Annual Insurance",
                min_value=0.0,
                value=float(expenses.annual_insurance),
                step=100.0,
            )
            monthly_hoa = st.number_input(
                "Monthly HOA",
                min_value=0.0,
                value=float(expenses.monthly_hoa),
                step=25.0,
            )
            monthly_property_management = st.number_input(
                "Monthly Property Management",
                min_value=0.0,
                value=float(expenses.monthly_property_management),
                step=25.0,
            )
        with col2:
            monthly_maintenance_reserve = st.number_input(
                "Monthly Maintenance / Reserve",
                min_value=0.0,
                value=float(expenses.monthly_maintenance_reserve),
                step=25.0,
            )
            monthly_owner_paid_utilities = st.number_input(
                "Monthly Owner-Paid Utilities",
                min_value=0.0,
                value=float(expenses.monthly_owner_paid_utilities),
                step=25.0,
            )
            monthly_other_expenses = st.number_input(
                "Other Monthly Expenses",
                min_value=0.0,
                value=float(expenses.monthly_other_expenses),
                step=25.0,
            )
            rent_ready_repairs = st.number_input(
                "One-Time Rent-Ready Repairs",
                min_value=0.0,
                value=float(verdict_inputs.rent_ready_repairs),
                step=500.0,
                help="Use this for small make-ready work. Heavy rehab is out of scope for this workflow.",
            )

        if st.form_submit_button("Save Expenses & Continue"):
            expenses.annual_property_taxes = annual_property_taxes
            expenses.annual_insurance = annual_insurance
            expenses.monthly_hoa = monthly_hoa
            expenses.monthly_property_management = monthly_property_management
            expenses.monthly_maintenance_reserve = monthly_maintenance_reserve
            expenses.monthly_owner_paid_utilities = monthly_owner_paid_utilities
            expenses.monthly_other_expenses = monthly_other_expenses
            verdict_inputs.rent_ready_repairs = rent_ready_repairs

            missing = get_missing_fields_for_step("expenses", deal_profile)
            if missing:
                st.warning(f"Complete the required fields before continuing: {', '.join(missing)}")
            else:
                _go_to_next_step()
                st.rerun()

    if st.button("Back to Financing"):
        _go_to_previous_step()
        st.rerun()


def _render_verdict_step(deal_profile) -> None:
    render_verdict_summary(deal_profile, title="Passive Rental Verdict")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Back to Expenses"):
            _go_to_previous_step()
            st.rerun()
    with action_col2:
        if st.button("Start Over"):
            st.session_state.deal_profile = type(deal_profile)()
            st.session_state.deal_wizard_step = 0
            st.rerun()


def show_deal_verdict_wizard() -> None:
    """Displays the primary guided workflow for single-deal passive rental analysis."""
    if "deal_wizard_step" not in st.session_state:
        st.session_state.deal_wizard_step = 0

    step_index = st.session_state.deal_wizard_step
    step_key, step_label = WIZARD_STEPS[step_index]
    deal_profile = st.session_state.deal_profile

    _show_step_header(step_label, step_index)

    if step_key == "property":
        _render_property_step(deal_profile)
    elif step_key == "rent":
        _render_rent_step(deal_profile)
    elif step_key == "financing":
        _render_financing_step(deal_profile)
    elif step_key == "expenses":
        _render_expenses_step(deal_profile)
    else:
        _render_verdict_step(deal_profile)
