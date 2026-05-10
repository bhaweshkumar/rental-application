"""Capital Markets Simulator page."""
import streamlit as st

from rental_platform.services.financing_service import calculate_loan_details, calculate_monthly_payment
from rental_platform.services.verdict_service import refresh_deal_calculations
from rental_platform.session import mark_profile_mutated
from rental_platform.utils import get_safe_index

LOAN_TYPE_OPTIONS = ["DSCR", "Conventional", "FHA", "Creative"]


def show_capital_markets_simulator() -> None:
    st.header("Step 3: Capital Markets Simulator")
    st.markdown(
        "Model the financing structure of your deal. "
        "This drives your mortgage payment, cash-to-close, and DSCR."
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    deal_profile = st.session_state["deal_profile"]
    cap = deal_profile.capital_markets_details
    acq = deal_profile.acquisition_details

    if acq.purchase_price <= 0:
        st.warning("Please complete Step 1 (Market & Regulatory) to set a purchase price first.")
        return

    purchase_price = float(acq.purchase_price)

    with st.container(border=True):
        st.subheader("Loan Parameters")
        loan_type = st.selectbox("Loan Type", LOAN_TYPE_OPTIONS,
            index=get_safe_index(LOAN_TYPE_OPTIONS, cap.loan_type))
        ltv_pct = st.slider("Loan-to-Value (LTV) %", 50, 97, int(cap.ltv_pct), 1)
        interest_rate_pct = st.number_input("Interest Rate (%)", min_value=0.0, max_value=20.0,
            value=float(cap.interest_rate_pct), step=0.125)
        term_years = st.selectbox("Loan Term (Years)", [30, 25, 20, 15],
            index=get_safe_index([30, 25, 20, 15], cap.term_years))
        closing_costs_pct = st.slider("Closing Costs (%)", 0, 7, int(cap.closing_costs_pct), 1)

    loan_amount, down_payment, closing_costs = calculate_loan_details(
        purchase_price, ltv_pct, closing_costs_pct
    )
    monthly_payment = calculate_monthly_payment(loan_amount, interest_rate_pct, term_years)
    annual_debt_service = monthly_payment * 12

    with st.container(border=True):
        st.subheader("Financing Summary")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Loan Amount", f"${loan_amount:,.0f}")
        m2.metric("Down Payment", f"${down_payment:,.0f}")
        m3.metric("Closing Costs", f"${closing_costs:,.0f}")
        m4.metric("Monthly P&I", f"${monthly_payment:,.0f}")
        st.metric("Annual Debt Service", f"${annual_debt_service:,.0f}")

    # Persist to canonical profile
    cap.loan_type = loan_type
    cap.ltv_pct = ltv_pct
    cap.interest_rate_pct = interest_rate_pct
    cap.term_years = term_years
    cap.closing_costs_pct = closing_costs_pct
    cap.loan_amount = loan_amount
    cap.down_payment = down_payment
    cap.closing_costs = closing_costs
    cap.monthly_payment = monthly_payment
    cap.annual_debt_service = annual_debt_service
    refresh_deal_calculations(deal_profile)
    mark_profile_mutated()

    st.success("Capital Markets model updated.")
    st.info("Next, proceed to **Underwriting Engine** to score the deal.")
