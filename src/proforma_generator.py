import streamlit as st
import pandas as pd
from dataclasses import asdict
from shared.models import ProformaAssumptions
from logic.proforma import generate_proforma

def show_proforma_generator():
    """Displays the UI for Feature 5: 3-Year Proforma & DCF Generator."""
    st.header("Step 5: Long-Term Proforma Generator")
    st.markdown("""
        A proforma is a financial projection of a property's performance over time. While Year 1 underwriting is critical for the initial decision, a proforma helps you understand the long-term viability and potential returns of your investment.
        
        **Why this is useful:** Real estate is a long-term game. This tool helps you model how rent growth, expense inflation, and debt paydown will affect your cash flow and returns over a multi-year holding period. It helps answer the question: "Is this a good investment not just today, but for the next 5-10 years?"
    """)

    deal_profile = st.session_state.deal_profile
    inputs = deal_profile.underwriting_inputs
    outputs = deal_profile.underwriting_outputs
    cap = deal_profile.capital_markets_details

    if outputs.noi <= 0:
        st.warning("Please complete 'Step 4: Underwriting Engine' to generate Year 1 NOI before creating a proforma.")
        return

    with st.container(border=True):
        st.subheader("Growth & Holding Assumptions")
        st.markdown("Set your assumptions for how income and expenses will change over time, and how long you plan to hold the property.")
        assumptions = deal_profile.proforma_assumptions

        col1, col2, col3 = st.columns(3)
        with col1:
            rent_growth_pct = st.slider("Annual Rent Growth (%)", 0.0, 10.0, assumptions.rent_growth_pct, 0.5, help="Your assumption for how much you can increase rent each year. Base this on market trends.")
        with col2:
            expense_growth_pct = st.slider("Annual Expense Growth (%)", 0.0, 10.0, assumptions.expense_growth_pct, 0.5, help="Your assumption for how much operating expenses (taxes, insurance, etc.) will increase each year. 2-3% is a common baseline.")
        with col3:
            holding_period_years = st.slider("Holding Period (Years)", 1, 10, assumptions.holding_period_years, 1, help="How many years you plan to own the property before selling.")

    # Update assumptions in session state for persistence
    deal_profile.proforma_assumptions = ProformaAssumptions(
        holding_period_years=holding_period_years,
        rent_growth_pct=rent_growth_pct,
        expense_growth_pct=expense_growth_pct,
    )

    # --- Calculations ---
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
            st.markdown("The table below shows the projected financial performance for each year of your holding period.")
            
            df = pd.DataFrame([asdict(p) for p in proforma_data])
            df = df.set_index('year')
            
            formatted_df = df.style.format({
                "gross_potential_rent": "${:,.0f}", "vacancy_loss": "(${:,.0f})",
                "effective_gross_income": "${:,.0f}", "operating_expenses": "(${:,.0f})",
                "noi": "${:,.0f}", "debt_service": "(${:,.0f})",
                "cash_flow_before_tax": "${:,.0f}",
            }).set_properties(**{'text-align': 'right'})

            st.dataframe(formatted_df, use_container_width=True)

        with st.container(border=True):
            st.subheader("Cash Flow Projection", divider="violet")
            st.markdown("This chart visualizes your projected annual cash flow before tax. An upward trend is a great sign!")
            st.bar_chart(df, y="cash_flow_before_tax")

    st.success("Proforma projection updated.")
    st.info("Next, proceed to **Tax & Refinance** to explore tax benefits.")