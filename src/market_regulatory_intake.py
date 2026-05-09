import streamlit as st

# A list of US states for the dropdown
US_STATES = [
    "", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

# Simplified risk score based on spec citation [cite: 104]
LANDLORD_FLEXIBILITY_RISK = {
    "Texas": "Low Risk (e.g., 21-28 days eviction)",
    "Indiana": "Low Risk",
    "Alabama": "Low Risk",
    "New Jersey": "High Risk (e.g., long uncontested eviction durations)",
    "California": "High Risk (e.g., long uncontested eviction durations)",
    # This can be expanded with more research
}

def show_market_regulatory_intake():
    """
    Displays the UI for Feature 1: Market & Regulatory Intake.
    Allows user to input property details, market phase, and state.
    """
    st.header("Feature 1: Market & Regulatory Intake")
    st.markdown(
        "Enter the high-level details of the property and its market environment. "
        "This information forms the basis for the underwriting model."
    )

    # Use a form for better UX, grouping inputs together
    with st.form("market_intake_form"):
        st.subheader("Property Details")

        # Get existing values from session state to pre-fill the form
        deal = st.session_state.get('deal_profile', {})
        prop_details = deal.get('property_details', {})

        address = st.text_input(
            "Property Address",
            value=prop_details.get('address', ''),
            help="Enter the full property address."
        )

        asset_type_options = ['Single-Family', '2-Unit', '4-Unit', 'Commercial Multifamily']
        asset_type_index = asset_type_options.index(prop_details.get('asset_type', 'Single-Family')) if prop_details.get('asset_type') in asset_type_options else 0
        asset_type = st.selectbox(
            "Asset Type",
            options=asset_type_options,
            index=asset_type_index,
            help="Select the type of property."
        )

        col1, col2 = st.columns(2)
        with col1:
            sq_ft = st.number_input("Square Footage", min_value=0, value=prop_details.get('sq_ft', 1000), step=50, help="Total livable square footage.")
        with col2:
            year_built = st.number_input("Year Built", min_value=1800, max_value=2025, value=prop_details.get('year_built', 2000), step=1, help="The year the property was built.")

        st.subheader("Market & Regulatory Environment")

        market_phase_options = ['Recovery', 'Expansion', 'Hyper-Supply', 'Recession']
        market_phase_index = market_phase_options.index(prop_details.get('market_phase', 'Expansion')) if prop_details.get('market_phase') in market_phase_options else 0
        market_phase = st.selectbox("Market Phase", options=market_phase_options, index=market_phase_index, help="Select the current phase of the local real estate cycle.")

        state_index = US_STATES.index(prop_details.get('state', '')) if prop_details.get('state', '') in US_STATES else 0
        state = st.selectbox("State / Regulatory Tag", US_STATES, index=state_index, help="Select the state to apply a 'Landlord Flexibility' risk score.")

        # Display the risk score based on state selection
        if state and state in LANDLORD_FLEXIBILITY_RISK:
            st.info(f"**Landlord Flexibility Score:** {LANDLORD_FLEXIBILITY_RISK[state]}")
        elif state:
            st.warning("Risk score is not defined for this state in the current model.")

        submitted = st.form_submit_button("Save Property & Market Details")

        if submitted:
            # Update the session state with the form data
            st.session_state.deal_profile['property_details'] = {
                "address": address,
                "asset_type": asset_type,
                "sq_ft": sq_ft,
                "year_built": year_built,
                "market_phase": market_phase,
                "state": state
            }
            st.success("Property and Market details have been saved to the current deal profile!")
            
            # Optional: show the saved data for confirmation
            with st.expander("View Current Deal Profile Data"):
                st.json(st.session_state.deal_profile)