import streamlit as st
from shared.constants import (
    US_STATES,
    LANDLORD_FLEXIBILITY_RISK,
    ASSET_TYPE_OPTIONS,
    MARKET_PHASE_OPTIONS,
)
from shared.models import PropertyDetails
from shared.utils import get_safe_index


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

        # Get existing property details from the session state's data model
        prop_details = st.session_state.deal_profile.property_details

        address = st.text_input(
            "Property Address",
            value=prop_details.address,
            help="Enter the full property address."
        )

        asset_type = st.selectbox(
            "Asset Type",
            options=ASSET_TYPE_OPTIONS,
            index=get_safe_index(ASSET_TYPE_OPTIONS, prop_details.asset_type),
            help="Select the type of property."
        )

        col1, col2 = st.columns(2)
        with col1:
            sq_ft = st.number_input("Square Footage", min_value=0, value=prop_details.sq_ft, step=50, help="Total livable square footage.")
        with col2:
            year_built = st.number_input("Year Built", min_value=1800, max_value=2025, value=prop_details.year_built, step=1, help="The year the property was built.")

        st.subheader("Market & Regulatory Environment")

        market_phase = st.selectbox("Market Phase", options=MARKET_PHASE_OPTIONS, index=get_safe_index(MARKET_PHASE_OPTIONS, prop_details.market_phase), help="Select the current phase of the local real estate cycle.")

        state = st.selectbox("State / Regulatory Tag", US_STATES, index=get_safe_index(US_STATES, prop_details.state), help="Select the state to apply a 'Landlord Flexibility' risk score.")

        # Display the risk score based on state selection
        if state and state in LANDLORD_FLEXIBILITY_RISK:
            st.info(f"**Landlord Flexibility Score:** {LANDLORD_FLEXIBILITY_RISK[state]}")
        elif state:
            st.warning("Risk score is not defined for this state in the current model.")
        
        submitted = st.form_submit_button("Save Property & Market Details")

        if submitted:
            # Update the data model in the session state directly
            st.session_state.deal_profile.property_details = PropertyDetails(
                address=address,
                asset_type=asset_type,
                sq_ft=sq_ft,
                year_built=year_built,
                market_phase=market_phase,
                state=state
            )
            st.success("Property and Market details have been saved to the current deal profile!")
            
            # Optional: show the saved data for confirmation
            with st.expander("View Current Deal Profile Data"):
                st.json(st.session_state.deal_profile)