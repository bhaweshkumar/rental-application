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
    st.header("Step 2: Acquisition & Value-Add Modeling")
    st.markdown(
        """
        This wizard helps you model the two most critical components of your entry into a deal: the **Purchase Price** and the **Rehabilitation Budget**. 
        Accurately estimating these costs is fundamental to understanding your all-in cost and potential for creating equity.
        
        **Why this is useful:** This isn't just about cost; it's about strategy. Are you buying a turnkey property or creating value through renovation? This tool helps you quantify that decision.
        """
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    # Check if property details are available, especially sq_ft
    deal_profile = st.session_state.deal_profile
    sq_ft = deal_profile.property_details.sq_ft

    if not sq_ft or sq_ft <= 0:
        st.warning("Please complete 'Step 1: Market & Property Fundamentals' first and enter a valid Square Footage (> 0) to enable rehab calculations.")
        return

    acq_details = deal_profile.acquisition_details

    with st.container(border=True):
        st.subheader("Acquisition Costs")
        st.markdown("Define the price you pay to acquire the property itself.")
        purchase_price = st.number_input(
            "Listing/Purchase Price",
            min_value=0,
            value=acq_details.purchase_price,
            step=5000,
            help="Enter the base acquisition cost for the property. This is the starting point for all financial calculations. [cite: 85]",
        )

    with st.container(border=True):
        st.subheader("Rehabilitation Estimator")
        st.markdown(f"Estimate the cost to bring the property to a rent-ready or after-repair condition. Based on **{sq_ft:,} sq ft**.")

        rehab_options = list(REHAB_COSTS_PER_SQFT.keys())
        rehab_level = st.radio(
            "Select Rehab Level",
            options=rehab_options,
            index=get_safe_index(rehab_options, acq_details.rehab_level, default=1),
            horizontal=True,
            help="Use a cost-per-square-foot model to quickly estimate rehab costs. Choose the level that best describes the planned work. [cite: 96, 97, 98]",
        )

        contingency_pct = st.slider(
            "Contingency Buffer (%)",
            min_value=0,
            max_value=30,
            value=acq_details.contingency_pct,
            step=1,
            help="Add a buffer for unexpected costs. A 10-15% contingency is standard practice and highly recommended. [cite: 99]",
        )

        rehab_cost_per_sqft = REHAB_COSTS_PER_SQFT.get(rehab_level, 0)
        base_rehab_cost, _, total_rehab_budget = calculate_rehab_costs(sq_ft, rehab_level, contingency_pct)
        
        rehab_col1, rehab_col2 = st.columns(2)
        rehab_col1.metric("Estimated Base Rehab Cost", f"${base_rehab_cost:,.2f}", f"at ${rehab_cost_per_sqft}/sq ft")
        rehab_col2.metric("Total Estimated Rehab Budget", f"${total_rehab_budget:,.2f}", f"includes {contingency_pct}% contingency")

    with st.container(border=True):
        st.subheader("After Repair Value (ARV)")
        st.markdown("Define the expected market value of the property *after* all renovations are complete.")
        arv = st.number_input(
            "After Repair Value (ARV)",
            min_value=0,
            value=acq_details.arv,
            step=5000,
            help="The ARV is crucial for value-add strategies. It determines your potential equity capture. This should be based on comparable sales (comps) of similar, renovated properties. [cite: 85]",
        )

    # Update session state
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
    acq_details = st.session_state.deal_profile.acquisition_details
    if acq_details.purchase_price > 0 and acq_details.arv > 0:
        st.subheader("Value-Add & BRRRR Strategy Simulator", divider="blue")
        st.markdown("""
        This simulator helps you analyze the core components of a value-add or BRRRR (Buy, Rehab, Rent, Refinance, Repeat) strategy. 
        It calculates how much equity you can create and how much cash you can potentially pull out upon refinancing.
        """)

        st.markdown("##### Cash-Out Refinance Estimator")
        refi_defaults = st.session_state.deal_profile.other_details
        refi_ltv_pct = st.slider(
            "Refinance LTV (%)",
            min_value=50,
            max_value=85,
            value=refi_defaults.get("refi_ltv_pct", 75),
            step=1,
            help="Select the Loan-to-Value for the cash-out refinance. For investment properties, this is typically 70-75% of the ARV for DSCR loans."
        )
        refi_defaults["refi_ltv_pct"] = refi_ltv_pct

        brrrr = calculate_brrrr_metrics(
            purchase_price=acq_details.purchase_price,
            total_rehab_budget=acq_details.total_rehab_budget,
            arv=acq_details.arv,
            refi_ltv_pct=refi_ltv_pct
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Total All-In Cost", f"${brrrr.all_in_cost:,.0f}", help="Purchase Price + Total Rehab Budget")
        col2.metric("After Repair Value (ARV)", f"${acq_details.arv:,.0f}")
        col3.metric(
            "Potential Equity Capture",
            f"${brrrr.equity_capture:,.0f}",
            help="The equity created through forced appreciation (ARV - All-In Cost). This is your 'profit on paper'."
        )

        refi_col1, refi_col2, refi_col3 = st.columns(3)
        refi_col1.metric("New Loan Amount", f"${brrrr.refi_loan_amount:,.0f}", f"at {refi_ltv_pct}% of ARV")

        if brrrr.cash_out_proceeds >= 0:
            refi_col2.metric("Tax-Free Cash Pulled Out", f"${brrrr.cash_out_proceeds:,.0f}", help="New Loan Amount - All-In Cost. This is the 'Repeat' part of BRRRR.")
        else:
            refi_col2.metric("Cash Left in Deal", f"${abs(brrrr.cash_out_proceeds):,.0f}", help="The amount of your initial capital remaining in the property after refinancing. A lower number means a higher ROI.")
        
        if brrrr.all_in_cost > 0:
            roi_on_cost = (brrrr.equity_capture / brrrr.all_in_cost) * 100 if brrrr.all_in_cost > 0 else 0
            refi_col3.metric("Return on Cost", f"{roi_on_cost:.1f}%", help="(Equity Capture / All-In Cost). A measure of your value-add efficiency.")

    st.success("Acquisition and Rehab model updated.")
    st.info("Next, proceed to **Capital Markets** to model your financing.")
