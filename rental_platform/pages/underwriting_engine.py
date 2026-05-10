"""Underwriting Engine page."""
import streamlit as st

from rental_platform.services.verdict_service import refresh_deal_calculations
from rental_platform.session import mark_profile_mutated


def show_underwriting_engine() -> None:
    st.header("Step 4: The Institutional Underwriting Engine")
    st.markdown(
        "Underwriting evaluates the financial viability and risk of an investment. "
        "This engine calculates the 'Big Four' metrics institutional investors use to quickly score a deal."
    )

    deal_profile = st.session_state["deal_profile"]
    acq = deal_profile.acquisition_details
    cap = deal_profile.capital_markets_details

    if acq.purchase_price <= 0 or cap.annual_debt_service <= 0:
        st.warning("Please complete Steps 1–3 (Market, Acquisition, Capital Markets) before underwriting.")
        return

    st.caption("Changes save automatically and refresh the shared deal state.")

    with st.container(border=True):
        st.subheader("Income & Expense Assumptions")
        vi = deal_profile.verdict_inputs
        baseline_gross_rent = max(vi.monthly_rent + vi.monthly_other_income, 0)
        monthly_gross_rent = st.number_input("Projected Monthly Gross Rent", min_value=0,
            value=int(baseline_gross_rent), step=100)
        vacancy_pct = st.slider("Vacancy Rate (%)", 0, 30, int(vi.vacancy_pct), 1)

        implied_opex = deal_profile.underwriting_inputs.opex_pct
        st.info(
            f"Operating expenses are pulled from shared line-item inputs. "
            f"Implied OpEx: **{implied_opex:.2f}%** of Effective Gross Income (EGI)."
        )

    vi.monthly_rent = max(monthly_gross_rent - vi.monthly_other_income, 0)
    vi.vacancy_pct = vacancy_pct
    refresh_deal_calculations(deal_profile)
    mark_profile_mutated()

    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        with st.container(border=True):
            st.subheader("The Big Four Deal Scorecard", divider="green")

            def dscr_color(v: float) -> str:
                return "green" if v >= 1.3 else ("orange" if v >= 1.2 else "red")

            color = dscr_color(outputs.dscr)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Net Operating Income (NOI)", f"${outputs.noi:,.0f}/yr")
            with c2:
                st.metric("Cap Rate (at Purchase)", f"{outputs.cap_rate_purchase:.2f}%")
            with c3:
                st.metric("Cash-on-Cash Return", f"{outputs.cash_on_cash_return:.2f}%")
            with c4:
                st.markdown(f"""
<div style="padding:10px;border-radius:5px;border:2px solid {color};">
<p style="font-size:0.8rem;color:#808495;margin:0">Debt Service Coverage Ratio (DSCR)</p>
<p style="font-size:1.75rem;font-weight:600;color:{color};margin:0">{outputs.dscr:.2f}</p>
<p style="font-size:0.8rem;color:#808495;margin:0">&gt; 1.20 required by most lenders</p>
</div>""", unsafe_allow_html=True)

    st.success("Underwriting scorecard updated.")
    st.info("Next, proceed to **Proforma & DCF** to project future performance.")
