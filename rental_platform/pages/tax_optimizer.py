"""Tax Optimizer page."""
import streamlit as st

from rental_platform.services.tax_service import calculate_depreciation
from rental_platform.session import mark_profile_mutated

DEPRECIATION_PERIOD = 27.5  # Residential rental property


def show_tax_optimizer() -> None:
    st.header("Step 6: Tax & Depreciation Optimizer")
    st.markdown(
        "Depreciation is one of the most powerful tax advantages of real estate investing. "
        "Model standard and accelerated depreciation strategies here."
    )

    deal_profile = st.session_state["deal_profile"]
    acq = deal_profile.acquisition_details
    tax_inputs = deal_profile.tax_optimization_inputs

    if acq.purchase_price <= 0:
        st.warning("Please complete Step 1 to set a purchase price first.")
        return

    land_value_pct = st.slider("Land Value (% of purchase price)", 5, 40, 20, 5,
        help="Land is not depreciable. Estimate what portion of the purchase price is land.")
    improvement_basis = acq.purchase_price * (1 - land_value_pct / 100.0)

    with st.container(border=True):
        st.subheader("Depreciation Method")
        enable_cost_seg = st.checkbox("Enable Cost Segregation (Accelerated Depreciation)",
            value=tax_inputs.enable_cost_segregation)
        if enable_cost_seg:
            col1, col2 = st.columns(2)
            with col1:
                cost_seg_5 = st.slider("5-Year Property (%)", 0, 40, tax_inputs.cost_seg_5_year_pct, 1)
            with col2:
                cost_seg_15 = st.slider("15-Year Property (%)", 0, 20, tax_inputs.cost_seg_15_year_pct, 1)
        else:
            cost_seg_5 = tax_inputs.cost_seg_5_year_pct
            cost_seg_15 = tax_inputs.cost_seg_15_year_pct

    tax_inputs.enable_cost_segregation = enable_cost_seg
    tax_inputs.cost_seg_5_year_pct = cost_seg_5
    tax_inputs.cost_seg_15_year_pct = cost_seg_15

    tax_outputs = calculate_depreciation(improvement_basis, DEPRECIATION_PERIOD, tax_inputs)
    deal_profile.tax_optimization_outputs = tax_outputs
    mark_profile_mutated()

    with st.container(border=True):
        st.subheader("Depreciation Summary")
        c1, c2, c3 = st.columns(3)
        c1.metric("Year 1 Bonus Depreciation", f"${tax_outputs.year_1_bonus_depreciation:,.0f}")
        c2.metric("Year 1 Standard Depreciation", f"${tax_outputs.year_1_standard_depreciation:,.0f}")
        c3.metric("Total Year 1 Depreciation", f"${tax_outputs.total_year_1_depreciation:,.0f}")
        st.metric("Annual Depreciation (Yr 2+)", f"${tax_outputs.annual_std_depreciation_after_y1:,.0f}")

    st.success("Tax model updated.")
    st.info("Next, proceed to **Profit Allocation** to model cash distribution.")
