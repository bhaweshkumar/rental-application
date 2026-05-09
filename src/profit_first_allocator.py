import streamlit as st
from shared.models import ProfitFirstInputs
from logic.profit_first import calculate_profit_first_allocations

def show_profit_first_allocator():
    """Displays the UI for Feature 7: 'Profit First' Cash Allocation."""
    st.header("Feature 7: 'Profit First' Cash Allocation")
    st.markdown(
        "Model the behavioral cash management system by allocating gross income to dedicated accounts **before** paying expenses."
    )

    deal_profile = st.session_state.deal_profile
    monthly_gross_rent = deal_profile.underwriting_inputs.monthly_gross_rent

    if monthly_gross_rent <= 0:
        st.warning("Please set a 'Projected Monthly Gross Rent' in Feature 4 before using the Profit First allocator.")
        return

    st.info(f"Modeling based on a Monthly Gross Rent of **${monthly_gross_rent:,.0f}**.")

    with st.form("profit_first_form"):
        st.subheader("Target Allocation Percentages (TAPs)")
        inputs = deal_profile.profit_first_inputs

        col1, col2, col3 = st.columns(3)
        with col1:
            profit_tap_pct = st.slider("Profit %", 0, 100, inputs.profit_tap_pct, 1)
        with col2:
            owners_pay_tap_pct = st.slider("Owner's Pay %", 0, 100, inputs.owners_pay_tap_pct, 1)
        with col3:
            tax_tap_pct = st.slider("Tax %", 0, 100, inputs.tax_tap_pct, 1)
        
        total_tap = profit_tap_pct + owners_pay_tap_pct + tax_tap_pct
        if total_tap > 100:
            st.error(f"Total allocation ({total_tap}%) exceeds 100% of income. This is not sustainable.")
        else:
            st.progress(total_tap / 100.0, text=f"Total Allocation: {total_tap}%")

        submitted = st.form_submit_button("Run Allocation & Save TAPs")

        # --- Calculations ---
        current_taps = ProfitFirstInputs(
            profit_tap_pct=profit_tap_pct,
            owners_pay_tap_pct=owners_pay_tap_pct,
            tax_tap_pct=tax_tap_pct,
        )
        
        if submitted:
            outputs = calculate_profit_first_allocations(monthly_gross_rent, current_taps)
            deal_profile.profit_first_inputs = current_taps
            deal_profile.profit_first_outputs = outputs
            st.success("Profit First TAPs and allocations have been saved!")

    # --- Results Display ---
    outputs = deal_profile.profit_first_outputs
    if outputs.opex_allocation != 0 or outputs.profit_allocation != 0 or outputs.owners_pay_allocation != 0:
        st.subheader("Monthly Cash Sweep Allocations", divider="cyan")
        
        rcol1, rcol2, rcol3, rcol4 = st.columns(4)
        rcol1.metric("Profit Account", f"${outputs.profit_allocation:,.2f}")
        rcol2.metric("Owner's Pay Account", f"${outputs.owners_pay_allocation:,.2f}")
        rcol3.metric("Tax Account", f"${outputs.tax_allocation:,.2f}")
        
        rcol4.metric(
            "Operating Expenses (OpEx) Account", 
            f"${outputs.opex_allocation:,.2f}", 
            help="The residual cash available to run the property."
        )