import streamlit as st
import pandas as pd
from shared.constants import REHAB_COSTS_PER_SQFT
from shared.models import AcquisitionDetails
from shared.utils import get_safe_index
from logic.rehab import calculate_rehab_costs
from logic.brrrr import calculate_brrrr_metrics
from logic.verdict import refresh_deal_calculations

def show_acquisition_rehab_modeler():
    """
    Displays the UI for Feature 2: Acquisition & Rehab Modeler.
    Allows user to input purchase price, rehab costs, and ARV.
    """
    st.header("Feature 2: Acquisition & Rehab Modeler")
    st.markdown(
        "Input the acquisition costs, estimate rehabilitation expenses, and define the After Repair Value (ARV). "
        "This is a critical step for value-add and BRRRR strategies."
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    # Check if property details are available, especially sq_ft
    deal_profile = st.session_state.deal_profile
    sq_ft = deal_profile.property_details.sq_ft

    if not sq_ft or sq_ft <= 0:
        st.warning("Please complete 'Feature 1: Market & Regulatory Intake' first and enter a valid Square Footage (> 0) to enable rehab calculations.")
        return

    st.subheader("Acquisition Costs")

    acq_details = deal_profile.acquisition_details

    purchase_price = st.number_input(
        "Listing/Purchase Price",
        min_value=0,
        value=acq_details.purchase_price,
        step=5000,
        help="Enter the base acquisition cost for the property. [cite: 85]",
    )

    st.subheader("Rehabilitation Estimator")
    st.markdown(f"Based on **{sq_ft:,} sq ft** from Property Details.")

    rehab_options = list(REHAB_COSTS_PER_SQFT.keys())
    rehab_level = st.radio(
        "Select Rehab Level",
        options=rehab_options,
        index=get_safe_index(rehab_options, acq_details.rehab_level, default=1),
        horizontal=True,
        help="Estimate rehab costs based on a cost-per-square-foot model. [cite: 96, 97, 98]",
    )

    contingency_pct = st.slider(
        "Contingency Buffer (%)",
        min_value=0,
        max_value=30,
        value=acq_details.contingency_pct,
        step=1,
        help="Add a buffer for unexpected costs. Default is 10-15%. [cite: 99]",
    )

    rehab_cost_per_sqft = REHAB_COSTS_PER_SQFT.get(rehab_level, 0)
    base_rehab_cost, _, total_rehab_budget = calculate_rehab_costs(sq_ft, rehab_level, contingency_pct)
    st.metric("Estimated Base Rehab Cost", f"${base_rehab_cost:,.2f}", f"at ${rehab_cost_per_sqft}/sq ft")
    st.metric("Total Estimated Rehab Budget", f"${total_rehab_budget:,.2f}", f"includes {contingency_pct}% contingency")

    st.subheader("Valuation")
    arv = st.number_input(
        "After Repair Value (ARV)",
        min_value=0,
        value=acq_details.arv,
        step=5000,
        help="The estimated market value of the property after all repairs are completed. [cite: 85]",
    )

    st.session_state.deal_profile.acquisition_details = AcquisitionDetails(
        purchase_price=purchase_price,
        rehab_level=rehab_level,
        rehab_cost_per_sqft=rehab_cost_per_sqft,
        base_rehab_cost=base_rehab_cost,
        contingency_pct=contingency_pct,
        total_rehab_budget=total_rehab_budget,
        arv=arv,
    )
    refresh_deal_calculations(st.session_state.deal_profile)

    # --- BRRRR / Value-Add Strategy Tracker ---
    # This section is displayed outside the form and reads from the current session state.
    acq_details = st.session_state.deal_profile.acquisition_details

    # Only show the tracker if a purchase price has been established.
    if acq_details.purchase_price > 0:
        st.subheader("BRRRR / Value-Add Strategy Tracker", divider="blue")

        st.markdown("##### Cash-Out Refinance Estimator")
        refi_defaults = st.session_state.deal_profile.other_details
        refi_ltv_pct = st.slider(
            "Refinance LTV (%)",
            min_value=50,
            max_value=85,
            value=refi_defaults.get("refi_ltv_pct", 75),
            step=1,
            help="Select the Loan-to-Value for the cash-out refinance, typically 75% for DSCR loans."
        )
        refi_defaults["refi_ltv_pct"] = refi_ltv_pct

        # Call the tested business logic
        brrrr = calculate_brrrr_metrics(
            purchase_price=acq_details.purchase_price,
            total_rehab_budget=acq_details.total_rehab_budget,
            arv=acq_details.arv,
            refi_ltv_pct=refi_ltv_pct
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total All-In Cost", f"${brrrr.all_in_cost:,.0f}")
        col2.metric("After Repair Value (ARV)", f"${acq_details.arv:,.0f}")
        col3.metric(
            "Potential Equity Capture",
            f"${brrrr.equity_capture:,.0f}",
            help="The equity created through forced appreciation (ARV - All-In Cost)."
        )

        st.markdown("##### Equity Capture Visual")
        chart_data = pd.DataFrame(
            {"Value": [brrrr.all_in_cost, acq_details.arv]},
            index=["All-In Cost", "After Repair Value (ARV)"],
        )
        st.bar_chart(chart_data)

        refi_col1, refi_col2 = st.columns(2)
        refi_col1.metric("New Loan Amount", f"${brrrr.refi_loan_amount:,.0f}", f"at {refi_ltv_pct}% of ARV")

        if brrrr.cash_out_proceeds >= 0:
            refi_col2.metric("Tax-Free Cash Pulled Out", f"${brrrr.cash_out_proceeds:,.0f}", help="New Loan Amount - All-In Cost")
        else:
            refi_col2.metric("Cash Left in Deal", f"${abs(brrrr.cash_out_proceeds):,.0f}", help="The amount of initial capital remaining in the property after refinancing.")
