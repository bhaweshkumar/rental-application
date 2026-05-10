"""Settings & Integrations page."""
import streamlit as st

from rental_platform.services.settings_service import load_settings, save_settings

SETTINGS_FILE = "settings.json"


def show_settings_page() -> None:
    st.header("Settings & Integrations")
    st.markdown("Configure application defaults and third-party integrations.")

    settings = load_settings(SETTINGS_FILE)

    with st.container(border=True):
        st.subheader("Deal Defaults")
        default_vacancy = st.slider("Default Vacancy Rate (%)", 0, 20,
            int(settings.get("default_vacancy_pct", 5)), 1)
        default_ltv = st.slider("Default LTV (%)", 50, 97,
            int(settings.get("default_ltv_pct", 75)), 1)
        default_interest = st.number_input("Default Interest Rate (%)", 0.0, 20.0,
            float(settings.get("default_interest_rate_pct", 7.5)), 0.125)

    if st.button("Save Settings", use_container_width=True):
        save_settings({
            "default_vacancy_pct": default_vacancy,
            "default_ltv_pct": default_ltv,
            "default_interest_rate_pct": default_interest,
        }, SETTINGS_FILE)
        st.success("Settings saved.")
