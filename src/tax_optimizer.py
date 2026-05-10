import streamlit as st
from shared.models import TaxOptimizationInputs, TaxOptimizationOutputs
from logic.tax import calculate_depreciation

def show_tax_optimizer():
    """Displays the UI for Feature 6: Tax Optimization."""
    st.header("Step 6: Tax Benefit Optimizer")
    st.markdown("""
        Depreciation is a powerful, non-cash expense that can significantly reduce your taxable income from a rental property. This wizard helps you model this benefit, including the advanced strategy of a Cost Segregation study.
        
        **Why this is useful:** Real estate offers unique tax advantages. Understanding depreciation can mean the difference between paying taxes on your cash flow and receiving a "paper loss" that can offset other income. This is a key part of maximizing your after-tax returns.
        
        *Disclaimer: This is for educational modeling only and is not tax advice. Consult a qualified professional.*
    """)

    deal_profile = st.session_state.deal_profile
    acq = deal_profile.acquisition_details
    prop = deal_profile.property_details

    if acq.purchase_price <= 0:
        st.warning("Please set a 'Listing/Purchase Price' in Step 2 before modeling tax optimization.")
        return

    with st.form("tax_form"):
        with st.container(border=True):
            st.subheader("Depreciation Assumptions")
            inputs = deal_profile.tax_optimization_inputs

            land_value_pct = st.slider(
                "Land Value as % of Purchase Price", 0, 50, deal_profile.other_details.get('land_value_pct', 20), 1,
                help="The IRS does not allow you to depreciate land. You must separate the value of the building from the land. A common estimate is 20% of the purchase price, but this can vary greatly by location."
            )
            
            st.markdown("---")
            st.subheader("Advanced: Cost Segregation")
            st.markdown("A Cost Segregation study is an engineering-based analysis that reclassifies parts of your property to accelerate depreciation, creating large tax deductions in the early years of ownership.")
            
            enable_cost_seg = st.toggle(
                "Enable Cost Segregation Study Model", value=inputs.enable_cost_segregation,
                help="This will model the effect of reclassifying components to take advantage of 100% bonus depreciation."
            )

            cost_seg_5_year_pct = inputs.cost_seg_5_year_pct
            cost_seg_15_year_pct = inputs.cost_seg_15_year_pct
            if enable_cost_seg:
                st.markdown("##### Cost Segregation Allocation")
                col1, col2 = st.columns(2)
                with col1:
                    cost_seg_5_year_pct = st.slider(
                        "% of Basis as 5-Year Property", 0, 40, inputs.cost_seg_5_year_pct, 1,
                        help="e.g., Appliances, carpet, fixtures. These components can be fully depreciated in Year 1 via bonus depreciation."
                    )
                with col2:
                    cost_seg_15_year_pct = st.slider(
                        "% of Basis as 15-Year Property", 0, 20, inputs.cost_seg_15_year_pct, 1,
                        help="e.g., Land improvements, parking lots. Also qualifies for 100% bonus depreciation."
                    )

        submitted = st.form_submit_button("Run Tax Analysis & Save")

        # --- Calculations ---
        improvement_basis = acq.purchase_price * (1 - (land_value_pct / 100.0))
        depreciation_period = 39.0 if prop.asset_type == 'Commercial Multifamily' else 27.5

        std_inputs = TaxOptimizationInputs(enable_cost_segregation=False)
        std_outputs = calculate_depreciation(improvement_basis, depreciation_period, std_inputs)

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
    with st.container(border=True):
        st.subheader("Depreciation Results", divider="orange")
        st.info(f"Depreciable Basis (Purchase Price - Land Value): **${improvement_basis:,.0f}** to be depreciated over **{depreciation_period}** years.")

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
                st.info("Enable Cost Segregation in the form above to see the powerful benefits of accelerated depreciation.")

    outputs = deal_profile.underwriting_outputs
    if outputs.noi > 0:
        with st.container(border=True):
            st.subheader("Estimated Tax Impact (Year 1)", divider="orange")
            tax_rate = st.slider("Your Marginal Tax Rate (%)", 0, 50, deal_profile.other_details.get('marginal_tax_rate', 24), 1, help="Your combined federal and state income tax rate. This determines the value of your deduction.")
            deal_profile.other_details['marginal_tax_rate'] = tax_rate
            
            cfbt = outputs.noi - deal_profile.capital_markets_details.annual_debt_service
            depreciation_deduction = deal_profile.tax_optimization_outputs.total_year_1_depreciation
            taxable_income = cfbt - depreciation_deduction
            tax_savings = depreciation_deduction * (tax_rate / 100.0)

            tcol1, tcol2, tcol3 = st.columns(3)
            tcol1.metric("Cash Flow Before Tax (CFBT)", f"${cfbt:,.0f}", help="The actual cash you receive from the property.")
            tcol2.metric("Year 1 Taxable Income", f"${taxable_income:,.0f}", help="CFBT - Depreciation Deduction. A negative value is a 'paper loss' that can often be used to offset other income.")
            tcol3.metric("Estimated Year 1 Tax Savings", f"${tax_savings:,.0f}", help="The amount of tax you save due to the depreciation deduction. Formula: Depreciation Deduction * Marginal Tax Rate")

    st.success("Tax optimization model updated.")
    st.info("Next, proceed to **Profit Allocation** to model your cash management strategy.")