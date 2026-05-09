import streamlit as st
from logic.settings import load_settings, save_settings
from logic.data_integration import DataSourceManager

CONFIG_FILE = "config.json"

def show_settings_page():
    """Displays the UI for Feature 9: Data Integration & Settings."""
    st.header("Feature 9: Data Integration & Settings")
    st.markdown("Manage API keys and other application settings.")

    settings = load_settings(CONFIG_FILE)

    st.subheader("API Key Management", divider="red")
    st.markdown(
        "This application uses the [RealtyMole API](https://rapidapi.com/realtymole/api/realtymole-rental-estimate) "
        "for property data. A free tier is available. Please enter your API key below."
    )

    api_key = st.text_input(
        "RealtyMole API Key",
        value=settings.get("realty_mole_api_key", ""),
        type="password",
        help="Your key is stored locally in config.json and is not shared."
    )

    if st.button("Save Settings"):
        settings["realty_mole_api_key"] = api_key
        save_settings(settings, CONFIG_FILE)
        st.success("Settings saved successfully!")
        st.rerun()

    st.subheader("Test API Connection", divider="red")
    
    if not settings.get("realty_mole_api_key"):
        st.warning("Please save an API key above to test the connection.")
    else:
        test_address = st.text_input(
            "Enter an address to test",
            "1600 Amphitheatre Parkway, Mountain View, CA"
        )
        if st.button("Fetch Property Data"):
            with st.spinner("Fetching data from RealtyMole..."):
                manager = DataSourceManager(settings)
                data = manager.get_property_data(test_address)
                if "error" in data:
                    st.error(f"Connection failed: {data['error']}")
                else:
                    st.success("Connection successful!")
                    st.json(data)