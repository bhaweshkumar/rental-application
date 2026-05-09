import streamlit as st

# Rehab costs per square foot based on spec [cite: 96, 97, 98]
REHAB_COSTS_PER_SQFT = {
    "None": 0,
    "Light (Cosmetic/Paint)": 20,  # Using average of $15-$25
    "Medium (Systems/Plumbing)": 37.5, # Using average of $25-$50
    "Heavy (Gut/Studs)": 65,
}

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

    # Check if property details are available, especially sq_ft
    deal_profile = st.session_state.get('deal_profile', {})
    property_details = deal_profile.get('property_details', {})
    sq_ft = property_details.get('sq_ft', 0)

    if not sq_ft or sq_ft <= 0:
        st.warning("Please complete 'Feature 1: Market & Regulatory Intake' first and enter a valid Square Footage (> 0) to enable rehab calculations.")
        return

    with st.form("acquisition_form"):
        st.subheader("Acquisition Costs")

        # Get existing values from session state
        acq_details = deal_profile.get('acquisition_details', {})

        purchase_price = st.number_input(
            "Listing/Purchase Price",
            min_value=0,
            value=acq_details.get('purchase_price', 250000),
            step=5000,
            help="Enter the base acquisition cost for the property. [cite: 85]"
        )

        st.subheader("Rehabilitation Estimator")
        st.markdown(f"Based on **{sq_ft:,} sq ft** from Property Details.")

        rehab_options = list(REHAB_COSTS_PER_SQFT.keys())
        rehab_level_default = acq_details.get('rehab_level', 'Light (Cosmetic/Paint)')
        rehab_level_index = rehab_options.index(rehab_level_default) if rehab_level_default in rehab_options else 1
        rehab_level = st.radio(
            "Select Rehab Level",
            options=rehab_options,
            index=rehab_level_index,
            horizontal=True,
            help="Estimate rehab costs based on a cost-per-square-foot model. [cite: 96, 97, 98]"
        )

        rehab_cost_per_sqft = REHAB_COSTS_PER_SQFT[rehab_level]
        base_rehab_cost = sq_ft * rehab_cost_per_sqft
        st.metric("Estimated Base Rehab Cost", f"${base_rehab_cost:,.2f}", f"at ${rehab_cost_per_sqft}/sq ft")

        contingency_pct = st.slider(
            "Contingency Buffer (%)",
            min_value=0,
            max_value=30,
            value=acq_details.get('contingency_pct', 15),
            step=1,
            help="Add a buffer for unexpected costs. Default is 10-15%. [cite: 99]"
        )

        contingency_amount = base_rehab_cost * (contingency_pct / 100.0)
        total_rehab_budget = base_rehab_cost + contingency_amount
        st.metric("Total Estimated Rehab Budget", f"${total_rehab_budget:,.2f}", f"includes {contingency_pct}% contingency")

        st.subheader("Valuation")
        arv = st.number_input(
            "After Repair Value (ARV)",
            min_value=0,
            value=acq_details.get('arv', 350000),
            step=5000,
            help="The estimated market value of the property after all repairs are completed. [cite: 85]"
        )

        submitted = st.form_submit_button("Save Acquisition & Rehab Details")

        if submitted:
            st.session_state.deal_profile['acquisition_details'] = {
                "purchase_price": purchase_price,
                "rehab_level": rehab_level,
                "rehab_cost_per_sqft": rehab_cost_per_sqft,
                "base_rehab_cost": base_rehab_cost,
                "contingency_pct": contingency_pct,
                "total_rehab_budget": total_rehab_budget,
                "arv": arv
            }
            st.success("Acquisition and Rehab details have been saved to the current deal profile!")

            with st.expander("View Current Deal Profile Data"):
                st.json(st.session_state.deal_profile)