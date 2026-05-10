import streamlit as st
from logic.verdict import refresh_deal_calculations
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
    st.header("Step 1: Market & Property Fundamentals")
    st.markdown(
        """
        Every great deal starts with understanding the fundamentals of the property and its environment. 
        This wizard helps you capture the essential details that form the foundation of your entire analysis.
        
        **Why this is important:** Getting these details right ensures all subsequent calculations—from rehab costs to long-term projections—are accurate and reliable.
        """
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    deal_profile = st.session_state.deal_profile
    prop_details = deal_profile.property_details

    with st.container(border=True):
        st.subheader("Property Details")
        st.markdown("Define the physical asset you are analyzing.")

        address = st.text_input(
            "Property Address",
            value=prop_details.address,
            help="Enter the full property address. This is used as the primary identifier for the deal.",
        )

        asset_type = st.selectbox(
            "Asset Type",
            options=ASSET_TYPE_OPTIONS,
            index=get_safe_index(ASSET_TYPE_OPTIONS, prop_details.asset_type),
            help="Select the type of property. This can influence rehab cost estimates and depreciation schedules.",
        )

        col1, col2 = st.columns(2)
        with col1:
            sq_ft = st.number_input(
                "Square Footage",
                min_value=0,
                value=prop_details.sq_ft,
                step=50,
                help="Total livable square footage. This is a key input for rehab cost estimations.",
            )
        with col2:
            year_built = st.number_input(
                "Year Built",
                min_value=1800,
                max_value=2025,
                value=prop_details.year_built,
                step=1,
                help="The year the property was built. Affects maintenance assumptions and potential for capital expenditures.",
            )

    with st.container(border=True):
        st.subheader("Market & Regulatory Environment")
        st.markdown("Assess the external factors that influence your investment's risk and potential.")

        market_phase = st.selectbox(
            "Market Phase",
            options=MARKET_PHASE_OPTIONS,
            index=get_safe_index(MARKET_PHASE_OPTIONS, prop_details.market_phase),
            help="Select the current phase of the local real estate cycle. This informs growth assumptions.",
        )

        state = st.selectbox(
            "State / Regulatory Tag",
            US_STATES,
            index=get_safe_index(US_STATES, prop_details.state),
            help="Select the state to apply a 'Landlord Flexibility' risk score. Legal environment is a critical, often overlooked, risk factor.",
        )

        if state and state in LANDLORD_FLEXIBILITY_RISK:
            st.info(f"**Landlord Flexibility Score for {state}:** {LANDLORD_FLEXIBILITY_RISK[state]}")
            with st.expander("What does this score mean?"):
                st.markdown("""
                This score is a qualitative measure of how "landlord-friendly" a state's laws are.
                - **High scores** (e.g., >70) typically indicate faster eviction processes and more landlord control.
                - **Low scores** (e.g., <40) may suggest stronger tenant protections, which can increase holding costs and risk during vacancies.
                This is a high-level indicator and not a substitute for legal advice.
                """)
        elif state:
            st.warning("Risk score is not defined for this state in the current model.")

    # Update deal profile
    deal_profile.property_details = PropertyDetails(
        address=address,
        asset_type=asset_type,
        sq_ft=sq_ft,
        year_built=year_built,
        market_phase=market_phase,
        state=state,
    )
    refresh_deal_calculations(deal_profile)

    st.success("Property and Market fundamentals have been updated.")
    st.info("Next, proceed to **Acquisition & Rehab** to model your entry costs.")

    with st.expander("View Current Deal Profile Data"):
        st.json(st.session_state.deal_profile)
