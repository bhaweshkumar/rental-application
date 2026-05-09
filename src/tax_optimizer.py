import streamlit as st
from shared.models import TaxOptimizationInputs, TaxOptimizationOutputs
from logic.tax import calculate_depreciation

def show_tax_optimizer():
    """Displays the UI for Feature 6: Tax Optimization."""
    st.header("Feature 6: Tax Optimization")
    st.markdown("Model the tax benefits of depreciation, including accelerated depreciation via Cost Segregation.")

    deal_profile = st.session_state.deal_profile
    acq = deal_profile.acquisition_details
    prop = deal_profile.property_details

    if acq.purchase_price <= 0:
        st.warning("Please set a 'Listing/Purchase Price' in Feature 2 before modeling tax optimization.")
        return

    with st.form("tax_form"):
        st.subheader("Depreciation Assumptions")
        inputs = deal_profile.tax_optimization_inputs

        land_value_pct = st.slider(
            "Land Value as % of Purchase Price", 0, 50, deal_profile.other_details.get('land_value_pct', 20), 1,
            help="Land is not depreciable. A common estimate is 20% of the purchase price."
        )
        
        enable_cost_seg = st.toggle(
            "Enable Cost Segregation Study", value=inputs.enable_cost_segregation,
            help="Reclassify components to accelerate depreciation with 100% bonus depreciation."
        )

        cost_seg_5_year_pct = inputs.cost_seg_5_year_pct
        cost_seg_15_year_pct = inputs.cost_seg_15_year_pct
        if enable_cost_seg:
            st.markdown("##### Cost Segregation Allocation")
            col1, col2 = st.columns(2)
            with col1:
                cost_seg_5_year_pct = st.slider(
                    "% of Basis as 5-Year Property", 0, 40, inputs.cost_seg_5_year_pct, 1,
                    help="e.g., Appliances, carpet, fixtures. Qualifies for 100% bonus depreciation."
                )
            with col2:
                cost_seg_15_year_pct = st.slider(
                    "% of Basis as 15-Year Property", 0, 20, inputs.cost_seg_15_year_pct, 1,
                    help="e.g., Land improvements, parking lots. Qualifies for 100% bonus depreciation."
                )

        submitted = st.form_submit_button("Run Tax Analysis & Save")

        # --- Calculations ---
        improvement_basis = acq.purchase_price * (1 - (land_value_pct / 100.0))
        depreciation_period = 39.0 if prop.asset_type == 'Commercial Multifamily' else 27.5

        # Calculate standard depreciation for comparison
        std_inputs = TaxOptimizationInputs(enable_cost_segregation=False)
        std_outputs = calculate_depreciation(improvement_basis, depreciation_period, std_inputs)

        # Calculate accelerated depreciation if enabled
        accel_outputs = TaxOptimizationOutputs()
        if enable_cost_seg:
            accel_inputs = TaxOptimizationInputs(
                enable_cost_segregation=True,
                cost_seg_5_year_pct=cost_seg_5_year_pct,
                cost_seg_15_year_pct=cost_seg_15_year_pct,
            )
            accel_outputs = calculate_depreciation(improvement_basis, depreciation_period, accel_inputs)

        if submitted:
            deal_profile.tax_optimization_inputs = TaxOptimizationInputs(
                enable_cost_segregation=enable_cost_seg,
                cost_seg_5_year_pct=cost_seg_5_year_pct,
                cost_seg_15_year_pct=cost_seg_15_year_pct,
            )
            deal_profile.tax_optimization_outputs = accel_outputs if enable_cost_seg else std_outputs
            deal_profile.other_details['land_value_pct'] = land_value_pct
            st.success("Tax optimization analysis saved!")

    # --- Results Display ---
    st.subheader("Depreciation Results", divider="orange")
    st.info(f"Depreciable Basis (Purchase Price - Land Value): **${improvement_basis:,.0f}** over **{depreciation_period}** years.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Standard Depreciation")
        st.metric("Year 1 Depreciation Deduction", f"${std_outputs.total_year_1_depreciation:,.0f}")
        st.metric("Annual Deduction (Years 2+)", f"${std_outputs.annual_std_depreciation_after_y1:,.0f}")

    with col2:
        st.markdown("#### Accelerated (with Cost Segregation)")
        if enable_cost_seg:
            st.metric("Year 1 Bonus Depreciation", f"${accel_outputs.year_1_bonus_depreciation:,.0f}", help="100% write-off of 5 & 15-year property.")
            st.metric("Year 1 Standard Depreciation", f"${accel_outputs.year_1_standard_depreciation:,.0f}", help="Depreciation on remaining 27.5/39-year property.")
            st.metric("TOTAL Year 1 Deduction", f"${accel_outputs.total_year_1_depreciation:,.0f}", delta=f"${accel_outputs.total_year_1_depreciation - std_outputs.total_year_1_depreciation:,.0f} vs. Standard")
        else:
            st.info("Enable Cost Segregation to see accelerated depreciation benefits.")

    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        st.subheader("Estimated Tax Impact", divider="orange")
        tax_rate = st.slider("Your Marginal Tax Rate (%)", 0, 50, deal_profile.other_details.get('marginal_tax_rate', 24), 1)
        deal_profile.other_details['marginal_tax_rate'] = tax_rate
        
        cfbt = outputs.noi - deal_profile.capital_markets_details.annual_debt_service
        depreciation_deduction = deal_profile.tax_optimization_outputs.total_year_1_depreciation
        taxable_income = cfbt - depreciation_deduction
        tax_savings = depreciation_deduction * (tax_rate / 100.0)

        tcol1, tcol2, tcol3 = st.columns(3)
        tcol1.metric("Cash Flow Before Tax (CFBT)", f"${cfbt:,.0f}")
        tcol2.metric("Year 1 Taxable Income", f"${taxable_income:,.0f}", help="CFBT - Depreciation Deduction. A negative value is a 'paper loss'.")
        tcol3.metric("Estimated Year 1 Tax Savings", f"${tax_savings:,.0f}", help="Depreciation Deduction * Marginal Tax Rate")