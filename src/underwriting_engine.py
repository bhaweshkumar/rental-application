import streamlit as st
from logic.verdict import refresh_deal_calculations

def show_underwriting_engine():
    """Displays the UI for Feature 4: The Institutional Underwriting Engine."""
    st.header("Step 4: The Institutional Underwriting Engine")
    st.markdown("""
        Underwriting is the process of evaluating the financial viability and risk of an investment. This is where we move from costs to profitability.
        This engine calculates the "Big Four" metrics that institutional investors use to quickly score a deal's potential.
        
        **Why this is useful:** These four metrics give you a multi-faceted view of the deal's health. A deal might look good on one metric (like Cap Rate) but fail on another (like DSCR). A professional investor looks at all four.
    """)

    deal_profile = st.session_state.deal_profile
    acq = deal_profile.acquisition_details
    cap = deal_profile.capital_markets_details

    # Check for dependencies from previous features
    if acq.purchase_price <= 0 or cap.annual_debt_service <= 0:
        st.warning("Please complete 'Step 2: Acquisition' and 'Step 3: Capital Markets' before underwriting.")
        return

    st.caption("Changes save automatically and refresh the shared deal state.")
    
    with st.container(border=True):
        st.subheader("Income & Expense Assumptions")
        st.markdown("Define your projections for income and the vacancy rate.")

        verdict_inputs = deal_profile.verdict_inputs
        baseline_gross_rent = max(verdict_inputs.monthly_rent + verdict_inputs.monthly_other_income, 0)
        monthly_gross_rent = st.number_input(
            "Projected Monthly Gross Rent",
            min_value=0,
            value=int(baseline_gross_rent),
            step=100,
            help="This is the total rent you expect to collect each month when the property is occupied.",
        )

        vacancy_pct = st.slider(
            "Vacancy Rate (%)",
            0,
            30,
            int(verdict_inputs.vacancy_pct),
            1,
            help="Percentage of gross rent lost to vacancy (empty unit) and credit loss (tenant not paying). 5-10% is a common assumption.",
        )
        
        implied_opex = deal_profile.underwriting_inputs.opex_pct
        st.info(
            f"Operating expenses are being pulled from the shared line-item inputs from the 'Deal Verdict Wizard' or other modules. "
            f"The implied Operating Expense (OpEx) is currently **{implied_opex:.2f}%** of Effective Gross Income (EGI)."
        )

    # Update state and refresh calculations
    verdict_inputs.monthly_rent = max(monthly_gross_rent - verdict_inputs.monthly_other_income, 0)
    verdict_inputs.vacancy_pct = vacancy_pct
    refresh_deal_calculations(deal_profile)

    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        with st.container(border=True):
            st.subheader("The 'Big Four' Deal Scorecard", divider="green")
            st.markdown("These are the four most important metrics for evaluating a rental property investment.")

            def get_dscr_color(dscr_value: float) -> str:
                if dscr_value >= 1.3: return "green"
                if dscr_value >= 1.2: return "orange"
                return "red"

            dscr_color = get_dscr_color(outputs.dscr)

            scol1, scol2, scol3, scol4 = st.columns(4)
            with scol1:
                st.metric("Net Operating Income (NOI)", f"${outputs.noi:,.0f}/yr")
                with st.expander("What is NOI?"):
                    st.markdown("NOI is the property's annual income after paying all operating expenses, but **before** paying the mortgage. It's a measure of the property's inherent profitability. Formula: `Income - Operating Expenses`")
            
            with scol2:
                st.metric("Cap Rate (at Purchase)", f"{outputs.cap_rate_purchase:.2f}%")
                with st.expander("What is Cap Rate?"):
                    st.markdown("The Capitalization Rate is the unlevered (all-cash) return on the asset. It's used to compare the profitability of different properties, regardless of financing. Formula: `NOI / Purchase Price`")

            with scol3:
                st.metric("Cash-on-Cash Return", f"{outputs.cash_on_cash_return:.2f}%")
                with st.expander("What is CoC Return?"):
                    st.markdown("This is your actual return on the cash you invested. It's a powerful measure of how hard your money is working for you. Formula: `(NOI - Debt Service) / Total Cash Invested`")
            
            with scol4:
                # Use custom HTML/CSS for the DSCR metric to apply border color based on risk
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border: 2px solid {dscr_color};">
                    <p style="font-size: 0.8rem; color: #808495; margin:0; padding:0;">Debt Service Coverage Ratio (DSCR)</p>
                    <p style="font-size: 1.75rem; font-weight: 600; color: {dscr_color}; margin:0; padding:0;">{outputs.dscr:.2f}</p>
                    <p style="font-size: 0.8rem; color: #808495; margin:0; padding:0;">{'> 1.20 is required by most lenders'}</p>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("What is DSCR?"):
                    st.markdown("The DSCR measures your ability to cover your mortgage payments from the property's income. Lenders look at this very closely. A value below 1.0 means you can't afford your mortgage. Most lenders require at least 1.20. Formula: `NOI / Annual Debt Service`")

    st.success("Underwriting scorecard updated.")
    st.info("Next, proceed to **Proforma & DCF** to project future performance.")
