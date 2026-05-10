import streamlit as st
from shared.models import ProfitFirstInputs
from logic.profit_first import calculate_profit_first_allocations

def show_profit_first_allocator():
    """Displays the UI for Feature 7: 'Profit First' Cash Allocation."""
    st.header("Step 7: 'Profit First' Cash Management")
    st.markdown(
        """
        'Profit First' is a behavioral cash management system designed to ensure profitability from the very first dollar of revenue. Instead of paying expenses first and keeping what's left (if anything), you allocate a percentage of your income to profit and other dedicated accounts *before* paying any bills.
        
        **Why this is useful for real estate:** This system forces you to build a more efficient, profitable rental business. By pre-allocating funds for profit, owner's compensation, and taxes, you are forced to run the property on the remaining operational budget. This encourages cost-efficiency and ensures you are paid first, not last.
        """
    )

    deal_profile = st.session_state.deal_profile
    # Using underwriting inputs for consistency with other modules
    monthly_gross_rent = deal_profile.underwriting_inputs.monthly_gross_rent

    if monthly_gross_rent <= 0:
        st.warning("Please set a 'Projected Monthly Gross Rent' in Step 4 (Underwriting Engine) before using the Profit First allocator.")
        return

    st.info(f"Modeling based on a Monthly Gross Rent of **${monthly_gross_rent:,.0f}**.")

    with st.form("profit_first_form"):
        with st.container(border=True):
            st.subheader("Target Allocation Percentages (TAPs)")
            st.markdown("Define what percentage of your gross rent you want to allocate to each 'bucket'. The remainder will be available for operating expenses.")
            inputs = deal_profile.profit_first_inputs

            col1, col2, col3 = st.columns(3)
            with col1:
                profit_tap_pct = st.slider("Profit %", 0, 100, inputs.profit_tap_pct, 1, help="For long-term reserves, capital improvements, or reinvestment.")
            with col2:
                owners_pay_tap_pct = st.slider("Owner's Pay %", 0, 100, inputs.owners_pay_tap_pct, 1, help="To compensate you for your time and effort.")
            with col3:
                tax_tap_pct = st.slider("Tax %", 0, 100, inputs.tax_tap_pct, 1, help="To set aside funds for future income tax liabilities.")
            
            total_tap = profit_tap_pct + owners_pay_tap_pct + tax_tap_pct
            if total_tap > 100:
                st.error(f"Total allocation ({total_tap}%) exceeds 100% of income. This is not sustainable. The property cannot support these allocations.")
            else:
                st.progress(total_tap / 100.0, text=f"Total Allocation to You/Reserves: {total_tap}%")

        submitted = st.form_submit_button("Run Allocation & Save TAPs")

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

    outputs = deal_profile.profit_first_outputs
    if outputs.opex_allocation != 0 or outputs.profit_allocation != 0 or outputs.owners_pay_allocation != 0:
        with st.container(border=True):
            st.subheader("Monthly Cash Sweep Allocations", divider="cyan")
            st.markdown("Based on your TAPs, here is how each month's gross rent would be allocated:")
            
            rcol1, rcol2, rcol3, rcol4 = st.columns(4)
            rcol1.metric("Profit Account", f"${outputs.profit_allocation:,.2f}", help="Goes to your profit/reinvestment account.")
            rcol2.metric("Owner's Pay Account", f"${outputs.owners_pay_allocation:,.2f}", help="Goes to your personal bank account.")
            rcol3.metric("Tax Account", f"${outputs.tax_allocation:,.2f}", help="Goes to a separate account to cover taxes.")
            
            opex_budget = outputs.opex_allocation
            opex_actual = deal_profile.verdict_outputs.annual_operating_expenses / 12
            opex_delta = opex_budget - opex_actual

            rcol4.metric(
                "Operating Expenses (OpEx) Account", 
                f"${opex_budget:,.2f}", 
                f"${opex_delta:,.2f} vs. est. expenses",
                help=f"The residual cash available to run the property. Your estimated monthly OpEx is ${opex_actual:,.2f}. A positive delta means your TAPs are sustainable; a negative delta means they are not."
            )