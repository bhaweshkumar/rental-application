"""Profit First Allocator page."""
import streamlit as st

from rental_platform.services.profit_first_service import calculate_profit_first_allocations
from rental_platform.session import mark_profile_mutated


def show_profit_first_allocator() -> None:
    st.header("Profit First Allocator")
    st.markdown(
        "Apply the Profit First methodology to your rental income. "
        "Set Target Allocation Percentages (TAPs) for each bucket."
    )

    deal_profile = st.session_state["deal_profile"]
    pf_inputs = deal_profile.profit_first_inputs
    vi = deal_profile.verdict_inputs
    gross_income = (vi.monthly_rent + vi.monthly_other_income) * 12

    if gross_income <= 0:
        st.warning("Please set rent income in the Deal Verdict Wizard or Underwriting Engine first.")
        return

    with st.container(border=True):
        st.subheader("Target Allocation Percentages (TAPs)")
        col1, col2, col3 = st.columns(3)
        with col1:
            profit_tap = st.slider("Profit (%)", 0, 30, pf_inputs.profit_tap_pct, 1)
        with col2:
            owners_pay_tap = st.slider("Owner Pay (%)", 0, 50, pf_inputs.owners_pay_tap_pct, 1)
        with col3:
            tax_tap = st.slider("Tax (%)", 0, 30, pf_inputs.tax_tap_pct, 1)

    pf_inputs.profit_tap_pct = profit_tap
    pf_inputs.owners_pay_tap_pct = owners_pay_tap
    pf_inputs.tax_tap_pct = tax_tap

    pf_outputs = calculate_profit_first_allocations(gross_income, pf_inputs)
    deal_profile.profit_first_outputs = pf_outputs
    mark_profile_mutated()

    with st.container(border=True):
        st.subheader(f"Annual Allocations (Gross: ${gross_income:,.0f})")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Profit", f"${pf_outputs.profit_allocation:,.0f}")
        c2.metric("Owner Pay", f"${pf_outputs.owners_pay_allocation:,.0f}")
        c3.metric("Tax Reserve", f"${pf_outputs.tax_allocation:,.0f}")
        c4.metric("OpEx", f"${pf_outputs.opex_allocation:,.0f}")

    st.success("Profit allocation updated.")
