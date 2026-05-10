"""
Rental Platform — main Streamlit entry point.

Run with:
  streamlit run app.py
"""
import streamlit as st

from rental_platform.pages.acquisition_rehab_modeler import show_acquisition_rehab_modeler
from rental_platform.pages.capital_markets_simulator import show_capital_markets_simulator
from rental_platform.pages.crm_funnel import show_crm_funnel
from rental_platform.pages.dashboard import show_dashboard
from rental_platform.pages.deal_summary_report import show_deal_summary_report
from rental_platform.pages.deal_verdict_wizard import show_deal_verdict_wizard
from rental_platform.pages.market_regulatory_intake import show_market_regulatory_intake
from rental_platform.pages.proforma_generator import show_proforma_generator
from rental_platform.pages.profit_first_allocator import show_profit_first_allocator
from rental_platform.pages.settings_page import show_settings_page
from rental_platform.pages.tax_optimizer import show_tax_optimizer
from rental_platform.pages.underwriting_engine import show_underwriting_engine
from rental_platform.session import initialize_session_state


def main() -> None:
    st.set_page_config(
        page_title="Passive Real Estate Underwriting Engine",
        layout="wide",
    )
    initialize_session_state()

    st.title("Passive Real Estate Underwriting & Evaluation Engine")
    st.markdown(
        "An institutional-grade evaluation of rental property investments, "
        "removing emotional bias and focusing on the mathematics of the deal."
    )

    pages = {
        "Overview": [
            st.Page(show_dashboard, title="Dashboard", icon="\U0001f3e0", default=True),
        ],
        "Deal Analysis": [
            st.Page(show_deal_verdict_wizard, title="Deal Verdict Wizard", icon="\u2696\ufe0f"),
            st.Page(show_market_regulatory_intake, title="Market & Regulatory", icon="\U0001f4c8"),
            st.Page(show_acquisition_rehab_modeler, title="Acquisition & Rehab", icon="\U0001f6e0\ufe0f"),
            st.Page(show_capital_markets_simulator, title="Capital Markets", icon="\U0001f3e6"),
            st.Page(show_underwriting_engine, title="Underwriting Engine", icon="\U0001f9ee"),
            st.Page(show_proforma_generator, title="Proforma & DCF", icon="\U0001f4c4"),
            st.Page(show_tax_optimizer, title="Tax & Refinance", icon="\U0001f4b0"),
            st.Page(show_profit_first_allocator, title="Profit Allocation", icon="\U0001f4b8"),
        ],
        "Reporting": [
            st.Page(show_deal_summary_report, title="Deal Summary Report", icon="\U0001f4ca"),
        ],
        "Management": [
            st.Page(show_crm_funnel, title="Lead Funnel (CRM)", icon="\U0001f4e7"),
            st.Page(show_settings_page, title="Settings & Integrations", icon="\u2699\ufe0f"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()
