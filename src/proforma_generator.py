import streamlit as st
import pandas as pd
from dataclasses import asdict
from shared.models import ProformaAssumptions
from logic.proforma import generate_proforma

def show_proforma_generator():
    """Displays the UI for Feature 5: 3-Year Proforma & DCF Generator."""
    st.header("Feature 5: 3-Year Proforma & DCF Generator")
    st.markdown("Project income, expenses, and cash flow over a multi-year holding period to forecast long-term viability.")

    deal_profile = st.session_state.deal_profile
    inputs = deal_profile.underwriting_inputs
    outputs = deal_profile.underwriting_outputs
    cap = deal_profile.capital_markets_details

    # Check for dependencies
    if outputs.noi <= 0:
        st.warning("Please complete 'Feature 4: Underwriting Engine' to generate Year 1 NOI before creating a proforma.")
        return

    st.subheader("Growth Assumptions")
    assumptions = deal_profile.proforma_assumptions

    col1, col2, col3 = st.columns(3)
    with col1:
        rent_growth_pct = st.slider("Annual Rent Growth (%)", 0.0, 10.0, assumptions.rent_growth_pct, 0.5)
    with col2:
        expense_growth_pct = st.slider("Annual Expense Growth (%)", 0.0, 10.0, assumptions.expense_growth_pct, 0.5)
    with col3:
        holding_period_years = st.slider("Holding Period (Years)", 1, 10, assumptions.holding_period_years, 1)

    # Update assumptions in session state for persistence
    deal_profile.proforma_assumptions = ProformaAssumptions(
        holding_period_years=holding_period_years,
        rent_growth_pct=rent_growth_pct,
        expense_growth_pct=expense_growth_pct,
    )

    # --- Calculations ---
    # Calculate initial values from the underwriting results
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
        st.subheader(f"{holding_period_years}-Year Proforma", divider="violet")
        
        # Convert list of dataclasses to a pandas DataFrame for display
        df = pd.DataFrame([asdict(p) for p in proforma_data])
        df = df.set_index('year')
        
        # Format for better readability
        formatted_df = df.style.format({
            "gross_potential_rent": "${:,.0f}", "vacancy_loss": "(${:,.0f})",
            "effective_gross_income": "${:,.0f}", "operating_expenses": "(${:,.0f})",
            "noi": "${:,.0f}", "debt_service": "(${:,.0f})",
            "cash_flow_before_tax": "${:,.0f}",
        }).set_properties(**{'text-align': 'right'})

        st.dataframe(formatted_df, use_container_width=True)

        st.subheader("Cash Flow Projection", divider="violet")
        st.bar_chart(df, y="cash_flow_before_tax")