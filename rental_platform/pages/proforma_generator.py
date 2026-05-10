"""Proforma Generator page."""
import streamlit as st
import pandas as pd
from dataclasses import asdict

from rental_platform.models import ProformaAssumptions
from rental_platform.services.proforma_service import generate_proforma
from rental_platform.session import mark_profile_mutated


def show_proforma_generator() -> None:
    st.header("Step 5: Long-Term Proforma Generator")
    st.markdown(
        "A proforma projects property performance over your holding period, "
        "helping you understand long-term viability and returns."
    )

    deal_profile = st.session_state["deal_profile"]
    inputs = deal_profile.underwriting_inputs
    outputs = deal_profile.underwriting_outputs
    cap = deal_profile.capital_markets_details

    if outputs.noi <= 0:
        st.warning("Please complete Step 4 (Underwriting Engine) before generating a proforma.")
        return

    with st.container(border=True):
        st.subheader("Growth & Holding Assumptions")
        assumptions = deal_profile.proforma_assumptions
        col1, col2, col3 = st.columns(3)
        with col1:
            rent_growth_pct = st.slider("Annual Rent Growth (%)", 0.0, 10.0, assumptions.rent_growth_pct, 0.5)
        with col2:
            expense_growth_pct = st.slider("Annual Expense Growth (%)", 0.0, 10.0, assumptions.expense_growth_pct, 0.5)
        with col3:
            holding_period_years = st.slider("Holding Period (Years)", 1, 10, assumptions.holding_period_years, 1)

    deal_profile.proforma_assumptions = ProformaAssumptions(
        holding_period_years=holding_period_years,
        rent_growth_pct=rent_growth_pct,
        expense_growth_pct=expense_growth_pct,
    )
    mark_profile_mutated()

    initial_gross_rent = inputs.monthly_gross_rent * 12
    egi_y1 = initial_gross_rent * (1 - (inputs.vacancy_pct / 100.0))
    initial_opex = egi_y1 * (inputs.opex_pct / 100.0)

    proforma_data = generate_proforma(
        initial_gross_rent=initial_gross_rent,
        initial_opex=initial_opex,
        vacancy_pct=inputs.vacancy_pct,
        annual_debt_service=cap.annual_debt_service,
        assumptions=deal_profile.proforma_assumptions,
    )

    if proforma_data:
        with st.container(border=True):
            st.subheader(f"{holding_period_years}-Year Proforma", divider="violet")
            df = pd.DataFrame([asdict(p) for p in proforma_data]).set_index("year")
            formatted_df = df.style.format({
                "gross_potential_rent": "${:,.0f}", "vacancy_loss": "(${:,.0f})",
                "effective_gross_income": "${:,.0f}", "operating_expenses": "(${:,.0f})",
                "noi": "${:,.0f}", "debt_service": "(${:,.0f})", "cash_flow_before_tax": "${:,.0f}",
            }).set_properties(**{"text-align": "right"})
            st.dataframe(formatted_df, use_container_width=True)

        with st.container(border=True):
            st.subheader("Cash Flow Projection", divider="violet")
            st.bar_chart(df, y="cash_flow_before_tax")

    st.success("Proforma projection updated.")
    st.info("Next, proceed to **Tax & Refinance** to explore tax benefits.")
