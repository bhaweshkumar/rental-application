import streamlit as st
from logic.verdict import refresh_deal_calculations

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

    st.caption("Changes save automatically and refresh the shared deal state.")
    st.subheader("Income Assumptions")

    verdict_inputs = deal_profile.verdict_inputs
    baseline_gross_rent = max(verdict_inputs.monthly_rent + verdict_inputs.monthly_other_income, 0)
    monthly_gross_rent = st.number_input(
        "Projected Monthly Gross Rent",
        min_value=0,
        value=int(baseline_gross_rent),
        step=100,
        help="This updates the guided verdict rent assumption while preserving any separate other-income value.",
    )

    vacancy_pct = st.slider(
        "Vacancy Rate (%)",
        0,
        30,
        int(verdict_inputs.vacancy_pct),
        1,
        help="Percentage of gross rent lost to vacancy and credit loss.",
    )

    verdict_inputs.monthly_rent = max(monthly_gross_rent - verdict_inputs.monthly_other_income, 0)
    verdict_inputs.vacancy_pct = vacancy_pct
    refresh_deal_calculations(deal_profile)

    # --- Deal Scorecard Display (outside the form) ---
    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        st.subheader("The 'Big Four' Deal Scorecard", divider="green")

        implied_opex = deal_profile.underwriting_inputs.opex_pct
        st.info(
            f"Operating expenses are being pulled from the shared line-item inputs. "
            f"Implied OpEx is currently {implied_opex:.2f}% of EGI."
        )

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
