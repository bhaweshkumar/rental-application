import streamlit as st
from shared.models import CapitalMarketsDetails
from shared.utils import get_safe_index
from logic.financing import calculate_loan_details, calculate_monthly_payment
from logic.verdict import refresh_deal_calculations

def show_capital_markets_simulator():
    """Displays the UI for Feature 3: Capital Markets & Leverage Simulator."""
    st.header("Feature 3: Capital Markets & Leverage Simulator")
    st.markdown(
        "Model different loan types to determine financing costs, down payment, and total cash needed to close."
    )

    deal_profile = st.session_state.deal_profile
    purchase_price = deal_profile.acquisition_details.purchase_price

    if purchase_price <= 0:
        st.warning("Please set a 'Listing/Purchase Price' in Feature 2 before modeling financing.")
        return

    st.info(f"Modeling based on a purchase price of **${purchase_price:,.0f}**.")
    st.caption("Changes save automatically and refresh the shared deal state.")

    st.subheader("Loan Assumptions")

    cap_details = deal_profile.capital_markets_details
    loan_type_options = ["DSCR", "Conventional", "FHA", "Creative"]

    loan_type = st.selectbox(
        "Loan Type",
        options=loan_type_options,
        index=get_safe_index(loan_type_options, cap_details.loan_type),
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        ltv_pct = st.slider("Loan-to-Value (LTV) %", 50, 97, cap_details.ltv_pct, 1)
    with col2:
        interest_rate_pct = st.slider(
            "Interest Rate %",
            3.0,
            12.0,
            cap_details.interest_rate_pct,
            0.125,
            format="%.3f%%",
        )
    with col3:
        term_options = [30, 25, 20, 15]
        term_years = st.selectbox(
            "Loan Term (Years)",
            term_options,
            index=get_safe_index(term_options, cap_details.term_years),
        )

    closing_costs_pct = st.slider(
        "Estimated Closing Costs % (of Purchase Price)",
        0,
        7,
        cap_details.closing_costs_pct,
        1,
        help="Includes lender fees, title, appraisal, etc. Typically 2-5%.",
    )

    loan_amount, down_payment, closing_costs = calculate_loan_details(
        purchase_price, ltv_pct, closing_costs_pct
    )
    monthly_payment = calculate_monthly_payment(
        loan_amount, interest_rate_pct, term_years
    )
    annual_debt_service = monthly_payment * 12
    total_cash_to_close = down_payment + closing_costs + deal_profile.acquisition_details.total_rehab_budget

    st.session_state.deal_profile.capital_markets_details = CapitalMarketsDetails(
        loan_type=loan_type,
        ltv_pct=ltv_pct,
        interest_rate_pct=interest_rate_pct,
        term_years=term_years,
        closing_costs_pct=closing_costs_pct,
        loan_amount=loan_amount,
        down_payment=down_payment,
        closing_costs=closing_costs,
        monthly_payment=monthly_payment,
        annual_debt_service=annual_debt_service,
    )
    st.session_state.deal_profile.other_details["wizard_financing_mode"] = "LTV %"
    refresh_deal_calculations(st.session_state.deal_profile)

    st.subheader("Financing Summary", divider="blue")

    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric("Loan Amount", f"${loan_amount:,.0f}")
    mcol2.metric("Down Payment", f"${down_payment:,.0f}", f"{100-ltv_pct}%")
    mcol3.metric("Monthly P&I", f"${monthly_payment:,.2f}")

    st.subheader("Total Capital Required", divider="blue")
    ccol1, ccol2, ccol3, ccol4 = st.columns(4)
    ccol1.metric("Down Payment", f"${down_payment:,.0f}")
    ccol2.metric("Closing Costs", f"${closing_costs:,.0f}")
    ccol3.metric("Rehab Budget", f"${deal_profile.acquisition_details.total_rehab_budget:,.0f}")
    ccol4.metric("TOTAL CASH TO CLOSE", f"${total_cash_to_close:,.0f}")
