"""Market & Regulatory Intake page."""
import streamlit as st

from rental_platform.constants import (
    ASSET_TYPE_OPTIONS,
    LANDLORD_FLEXIBILITY_RISK,
    MARKET_PHASE_OPTIONS,
    US_STATES,
)
from rental_platform.models import PropertyDetails
from rental_platform.services.verdict_service import refresh_deal_calculations
from rental_platform.session import mark_profile_mutated
from rental_platform.utils import get_safe_index


def show_market_regulatory_intake() -> None:
    st.header("Step 1: Market & Property Fundamentals")
    st.markdown(
        "Every great deal starts with understanding the fundamentals of the property "
        "and its environment. This wizard helps you capture the essential details that "
        "form the foundation of your entire analysis.\n\n"
        "**Why this is important:** Getting these details right ensures all subsequent "
        "calculations—from rehab costs to long-term projections—are accurate and reliable."
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    deal_profile = st.session_state["deal_profile"]
    prop = deal_profile.property_details

    with st.container(border=True):
        st.subheader("Property Details")
        st.markdown("Define the physical asset you are analysing.")

        address = st.text_input("Property Address", value=prop.address,
            help="Enter the full property address.")
        asset_type = st.selectbox("Asset Type", options=ASSET_TYPE_OPTIONS,
            index=get_safe_index(ASSET_TYPE_OPTIONS, prop.asset_type),
            help="Select the type of property.")

        col1, col2 = st.columns(2)
        with col1:
            sq_ft = st.number_input("Square Footage", min_value=0, value=prop.sq_ft,
                step=50, help="Total livable square footage.")
        with col2:
            year_built = st.number_input("Year Built", min_value=1800, max_value=2025,
                value=prop.year_built, step=1, help="The year the property was built.")

    with st.container(border=True):
        st.subheader("Market & Regulatory Environment")
        st.markdown("Assess the external factors that influence your investment.")

        market_phase = st.selectbox("Market Phase", options=MARKET_PHASE_OPTIONS,
            index=get_safe_index(MARKET_PHASE_OPTIONS, prop.market_phase),
            help="Select the current phase of the local real estate cycle.")
        state = st.selectbox("State / Regulatory Tag", US_STATES,
            index=get_safe_index(US_STATES, prop.state),
            help="Select the state to apply a Landlord Flexibility risk score.")

        if state and state in LANDLORD_FLEXIBILITY_RISK:
            st.info(f"**Landlord Flexibility Score for {state}:** {LANDLORD_FLEXIBILITY_RISK[state]}")
        elif state:
            st.warning("Risk score is not defined for this state in the current model.")

    # Write to canonical profile and signal the mutation to the session layer
    deal_profile.property_details = PropertyDetails(
        address=address,
        asset_type=asset_type,
        sq_ft=sq_ft,
        year_built=year_built,
        market_phase=market_phase,
        state=state,
    )
    refresh_deal_calculations(deal_profile)
    mark_profile_mutated()

    st.success("Property and Market fundamentals updated.")
    st.info("Next, proceed to **Acquisition & Rehab** to model your entry costs.")

    with st.expander("View Current Deal Profile Data"):
        st.json(st.session_state["deal_profile"])
