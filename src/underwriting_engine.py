import streamlit as st
from shared.models import UnderwritingInputs, UnderwritingOutputs
from logic.underwriting import (
    calculate_noi,
    calculate_cap_rate,
    calculate_dscr,
    calculate_cash_on_cash,
    calculate_total_cash_invested,
)

def show_underwriting_engine():
    """Displays the UI for Feature 4: The Institutional Underwriting Engine."""
    st.header("Feature 4: The Institutional Underwriting Engine")
    st.markdown("Calculate the 'Big Four' institutional metrics to score the deal's profitability and risk.")

    deal_profile = st.session_state.deal_profile
    acq = deal_profile.acquisition_details
    cap = deal_profile.capital_markets_details

    # Check for dependencies from previous features
    if acq.purchase_price <= 0 or cap.annual_debt_service <= 0:
        st.warning("Please complete 'Feature 2: Acquisition' and 'Feature 3: Capital Markets' before underwriting.")
        return

    with st.form("underwriting_form"):
        st.subheader("Income & Expense Assumptions")
        inputs = deal_profile.underwriting_inputs

        monthly_gross_rent = st.number_input("Projected Monthly Gross Rent", min_value=0, value=inputs.monthly_gross_rent, step=100)
        
        col1, col2 = st.columns(2)
        with col1:
            vacancy_pct = st.slider("Vacancy Rate (%)", 0, 30, inputs.vacancy_pct, 1, help="Percentage of gross rent lost to vacancy and credit loss.")
        with col2:
            opex_pct = st.slider("Operating Expenses (OpEx) % of EGI", 10, 60, inputs.opex_pct, 1, help="Includes taxes, insurance, maintenance, management, etc., as a percentage of Effective Gross Income.")

        # --- Live Calculations within the form ---
        annual_gross_rent = monthly_gross_rent * 12
        egi = annual_gross_rent * (1 - (vacancy_pct / 100.0))
        operating_expenses = egi * (opex_pct / 100.0)
        
        # Call the tested logic functions
        noi = calculate_noi(annual_gross_rent, vacancy_pct, operating_expenses)
        total_cash_invested = calculate_total_cash_invested(cap.down_payment, cap.closing_costs, acq.total_rehab_budget)
        cap_rate = calculate_cap_rate(noi, acq.purchase_price)
        dscr = calculate_dscr(noi, cap.annual_debt_service)
        coc_return = calculate_cash_on_cash(noi, cap.annual_debt_service, total_cash_invested)

        submitted = st.form_submit_button("Run Underwriting & Save")
        if submitted:
            deal_profile.underwriting_inputs = UnderwritingInputs(
                monthly_gross_rent=monthly_gross_rent, vacancy_pct=vacancy_pct, opex_pct=opex_pct,
            )
            deal_profile.underwriting_outputs = UnderwritingOutputs(
                noi=noi, cap_rate_purchase=cap_rate, dscr=dscr,
                cash_on_cash_return=coc_return, total_cash_invested=total_cash_invested,
            )
            st.success("Underwriting analysis complete and saved!")

    # --- Deal Scorecard Display (outside the form) ---
    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        st.subheader("The 'Big Four' Deal Scorecard", divider="green")

        def get_dscr_color(dscr_value: float) -> str:
            if dscr_value >= 1.3: return "green"
            if dscr_value >= 1.2: return "orange"
            return "red"

        dscr_color = get_dscr_color(outputs.dscr)

        scol1, scol2, scol3, scol4 = st.columns(4)
        scol1.metric("Net Operating Income (NOI)", f"${outputs.noi:,.0f}/yr")
        scol2.metric("Cap Rate (at Purchase)", f"{outputs.cap_rate_purchase:.2f}%")
        scol3.metric("Cash-on-Cash Return", f"{outputs.cash_on_cash_return:.2f}%")
        
        # Use custom HTML/CSS for the DSCR metric to apply border color based on risk
        scol4.markdown(f"""
        <div style="padding: 10px; border-radius: 5px; border: 2px solid {dscr_color};">
            <p style="font-size: 0.8rem; color: #808495; margin:0; padding:0;">Debt Service Coverage Ratio (DSCR)</p>
            <p style="font-size: 1.75rem; font-weight: 600; color: {dscr_color}; margin:0; padding:0;">{outputs.dscr:.2f}</p>
            <p style="font-size: 0.8rem; color: #808495; margin:0; padding:0;">{'> 1.20 is required'}</p>
        </div>
        """, unsafe_allow_html=True)