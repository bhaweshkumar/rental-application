import streamlit as st
import pandas as pd
from dataclasses import asdict
from logic.proforma import generate_proforma
from logic.verdict import refresh_deal_calculations
from verdict_summary import render_verdict_summary

def show_deal_summary_report():
    """Displays a consolidated summary report of the active deal."""
    st.header("Deal Summary Report")

    deal_profile = st.session_state.deal_profile
    refresh_deal_calculations(deal_profile)
    prop = deal_profile.property_details
    acq = deal_profile.acquisition_details
    cap = deal_profile.capital_markets_details
    uw_inputs = deal_profile.underwriting_inputs
    uw_outputs = deal_profile.underwriting_outputs
    tax_outputs = deal_profile.tax_optimization_outputs

    if not prop.address:
        st.warning("No active deal to report. Please load a deal from the CRM or fill out Feature 1.")
        return

    st.title(prop.address)
    st.caption(f"Status: {deal_profile.status}")
    st.markdown("---")

    if deal_profile.verdict_inputs.monthly_rent > 0 and acq.purchase_price > 0:
        render_verdict_summary(deal_profile, title="Guided Verdict Summary")
        st.markdown("---")

    # --- Section 1: Acquisition & Value-Add ---
    st.subheader("Acquisition & Value-Add Summary")
    acq_col1, acq_col2, acq_col3, acq_col4, acq_col5 = st.columns(5)
    acq_col1.metric("Purchase Price", f"${acq.purchase_price:,.0f}")
    acq_col2.metric("Rehab Budget", f"${acq.total_rehab_budget:,.0f}")
    
    all_in_cost = acq.purchase_price + acq.total_rehab_budget
    acq_col3.metric("Total All-In Cost", f"${all_in_cost:,.0f}")
    acq_col4.metric("After Repair Value (ARV)", f"${acq.arv:,.0f}")

    equity_capture = acq.arv - all_in_cost
    acq_col5.metric("Equity Capture", f"${equity_capture:,.0f}")
    st.markdown("---")

    # --- Section 2: Financing & Capital Required ---
    st.subheader("Financing & Capital Required")
    fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
    fin_col1.metric("Loan Type", cap.loan_type)
    fin_col2.metric("Loan Amount", f"${cap.loan_amount:,.0f}")
    fin_col3.metric("Down Payment", f"${cap.down_payment:,.0f}")
    fin_col4.metric("Total Cash to Close", f"${uw_outputs.total_cash_invested:,.0f}", help="Down Payment + Closing Costs + Rehab Budget")
    st.markdown("---")

    # --- Section 3: Core Underwriting Metrics ---
    st.subheader("Core Underwriting Metrics (Year 1)")
    uw_col1, uw_col2, uw_col3, uw_col4 = st.columns(4)
    uw_col1.metric("Net Operating Income (NOI)", f"${uw_outputs.noi:,.0f}/yr")
    uw_col2.metric("Cap Rate (Purchase)", f"{uw_outputs.cap_rate_purchase:.2f}%")
    uw_col3.metric("Cash-on-Cash Return", f"${uw_outputs.cash_on_cash_return:.2f}%")
    uw_col4.metric("DSCR", f"{uw_outputs.dscr:.2f}")
    st.markdown("---")

    # --- Section 4: Tax Benefits ---
    st.subheader("Tax Benefits (Year 1)")
    tax_col1, tax_col2, tax_col3 = st.columns(3)
    tax_col1.metric("Total Y1 Depreciation", f"${tax_outputs.total_year_1_depreciation:,.0f}")
    
    cfbt = uw_outputs.noi - cap.annual_debt_service
    taxable_income = cfbt - tax_outputs.total_year_1_depreciation
    tax_col2.metric("Taxable Income", f"${taxable_income:,.0f}", help="A negative value is a 'paper loss'.")

    tax_rate = deal_profile.other_details.get('marginal_tax_rate', 0)
    tax_savings = tax_outputs.total_year_1_depreciation * (tax_rate / 100.0)
    tax_col3.metric("Est. Tax Savings", f"${tax_savings:,.0f}", f"at {tax_rate}% rate")
    st.markdown("---")

    # --- Section 5: Proforma Snapshot ---
    st.subheader("Proforma Snapshot")
    if uw_outputs.noi > 0:
        initial_gross_rent = uw_inputs.monthly_gross_rent * 12
        egi_y1 = initial_gross_rent * (1 - (uw_inputs.vacancy_pct / 100.0))
        initial_opex = egi_y1 * (uw_inputs.opex_pct / 100.0)

        proforma_data = generate_proforma(
            initial_gross_rent=initial_gross_rent, initial_opex=initial_opex,
            vacancy_pct=uw_inputs.vacancy_pct, annual_debt_service=cap.annual_debt_service,
            assumptions=deal_profile.proforma_assumptions,
        )
        
        if proforma_data:
            df = pd.DataFrame([asdict(p) for p in proforma_data])
            df = df.set_index('year')
            
            st.markdown(f"**{deal_profile.proforma_assumptions.holding_period_years}-Year Cash Flow Projection**")
            st.bar_chart(df, y="cash_flow_before_tax")
    else:
        st.info("Run underwriting in Feature 4 to generate a proforma projection.")
