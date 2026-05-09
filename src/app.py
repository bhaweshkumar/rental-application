import streamlit as st
from market_regulatory_intake import show_market_regulatory_intake
from acquisition_rehab_modeler import show_acquisition_rehab_modeler

def initialize_session_state():
    """Initializes the session state for the application if not already done."""
    if 'deal_profile' not in st.session_state:
        st.session_state.deal_profile = {}


def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(
        page_title="Passive Real Estate Underwriting Engine",
        layout="wide"
    )

    initialize_session_state()

    st.title("Passive Real Estate Underwriting & Evaluation Engine")
    st.markdown("""
    This application provides an institutional-grade evaluation of rental property investments,
    removing emotional bias and focusing on the mathematics of the deal.
    """)

    # Sidebar for navigation based on features
    st.sidebar.title("Navigation")
    features = [
        "Home",
        "Feature 1: Market & Regulatory Intake",
        "Feature 2: Acquisition & Rehab Modeler",
        "Feature 3: Capital Markets & Leverage Simulator",
        "Feature 4: The Institutional Underwriting Engine",
        "Feature 5: 3-Year Proforma & DCF Generator",
        "Feature 6: BRRRR Refinance & Tax Optimization",
        "Feature 7: 'Profit First' Cash Allocation",
        "Feature 8: Automated Lead Funnel (CRM)",
        "Feature 9: Data Integration & Settings"
    ]
    selection = st.sidebar.radio("Go to", features)

    if selection == "Home":
        st.header("Welcome to the Underwriting Engine")
        st.info("Select a feature from the sidebar to begin analyzing a deal.")
        # In the future, this area can host a dashboard of saved deals.

    elif selection == "Feature 1: Market & Regulatory Intake":
        show_market_regulatory_intake()

    elif selection == "Feature 2: Acquisition & Rehab Modeler":
        show_acquisition_rehab_modeler()

    # Placeholder for feature implementations
    elif "Feature" in selection:
        st.header(selection)
        st.write(f"UI and logic for **{selection}** will be implemented here.")


if __name__ == "__main__":
    main()