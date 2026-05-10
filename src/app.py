import streamlit as st
from deal_verdict_wizard import show_deal_verdict_wizard
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
    if "deal_wizard_step" not in st.session_state:
        st.session_state.deal_wizard_step = 0


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
    
    def home_page():
        st.header("Welcome")
        st.info("Select a feature from the sidebar to begin analyzing a deal.")
        st.write("Dashboard content can be displayed here.")

    pages = {
        "Overview": [
            st.Page(home_page, title="Dashboard", icon="🏠", default=True)
        ],
        "Deal Analysis": [
            st.Page(show_deal_verdict_wizard, title="Deal Verdict Wizard", icon="⚖️"),
            st.Page(show_market_regulatory_intake, title="Market & Regulatory", icon="📈"),
            st.Page(show_acquisition_rehab_modeler, title="Acquisition & Rehab", icon="🛠️"),
            st.Page(show_capital_markets_simulator, title="Capital Markets", icon="🏦"),
            st.Page(show_underwriting_engine, title="Underwriting Engine", icon="🧮"),
            st.Page(show_proforma_generator, title="Proforma & DCF", icon="📄"),
            st.Page(show_tax_optimizer, title="Tax & Refinance", icon="💰"),
            st.Page(show_profit_first_allocator, title="Profit Allocation", icon="💸"),
        ],
        "Reporting": [
            st.Page(show_deal_summary_report, title="Deal Summary Report", icon="📊")
        ],
        "Management": [
            st.Page(show_crm_funnel, title="Lead Funnel (CRM)", icon="📧"),
            st.Page(show_settings_page, title="Settings & Integrations", icon="⚙️"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()
