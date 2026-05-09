import streamlit as st
from market_regulatory_intake import show_market_regulatory_intake
from acquisition_rehab_modeler import show_acquisition_rehab_modeler
from shared.models import DealProfile
from capital_markets_simulator import show_capital_markets_simulator
from underwriting_engine import show_underwriting_engine
from proforma_generator import show_proforma_generator
from tax_optimizer import show_tax_optimizer
from profit_first_allocator import show_profit_first_allocator
from crm_funnel import show_crm_funnel
from settings_page import show_settings_page
from deal_summary_report import show_deal_summary_report

def initialize_session_state():
    """Initializes the session state for the application if not already done."""
    if 'deal_profile' not in st.session_state:
        st.session_state.deal_profile = DealProfile()


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
    
    def show_placeholder_page(feature_name):
        st.header(feature_name)
        st.write(f"UI and logic for **{feature_name}** will be implemented here.")
    
    # A dictionary to map feature names to their corresponding functions
    # This makes the navigation logic cleaner and more scalable
    pages = {
        "Feature 1: Market & Regulatory Intake": show_market_regulatory_intake,
        "Feature 2: Acquisition & Rehab Modeler": show_acquisition_rehab_modeler,
        "Feature 3: Capital Markets & Leverage Simulator": show_capital_markets_simulator,
        "Feature 4: The Institutional Underwriting Engine": show_underwriting_engine,
        "Feature 5: 3-Year Proforma & DCF Generator": show_proforma_generator,
        "Feature 6: BRRRR Refinance & Tax Optimization": show_tax_optimizer,
        "Feature 7: 'Profit First' Cash Allocation": show_profit_first_allocator,
        "Feature 8: Automated Lead Funnel (CRM)": show_crm_funnel,
        "Feature 9: Data Integration & Settings": show_settings_page,
    }
    
    # --- Sidebar Navigation ---
    st.sidebar.title("Navigation")
    
    nav_options = ["Home", "Deal Summary Report"] + list(pages.keys())
    selection = st.sidebar.radio("Go to", nav_options)
    
    # --- Page Rendering ---
    if selection == "Deal Summary Report":
        show_deal_summary_report()
    elif selection in pages:
        pages[selection]()
    else: # Default to Home
        st.header("Welcome to the Underwriting Engine")
        st.info("Select a feature from the sidebar to begin analyzing a deal.")

if __name__ == "__main__":
    main()