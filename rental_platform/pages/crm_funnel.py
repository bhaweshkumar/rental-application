"""CRM Lead Funnel page."""
import streamlit as st

from rental_platform.services.crm_service import save_deals, load_deals
from rental_platform.session import mark_profile_mutated

DEALS_FILE = "deals.json"


def show_crm_funnel() -> None:
    st.header("Lead Funnel (CRM)")
    st.markdown("Manage and track deals through your acquisition pipeline.")

    deal_profile = st.session_state["deal_profile"]

    col_save, col_load = st.columns(2)

    with col_save:
        st.subheader("Save Current Deal")
        status = st.selectbox("Deal Status", ["Analysis", "Under Contract", "Closed", "Rejected"],
            index=["Analysis", "Under Contract", "Closed", "Rejected"].index(
                deal_profile.status if deal_profile.status in
                ["Analysis", "Under Contract", "Closed", "Rejected"] else "Analysis"
            ))
        if st.button("Save Deal", use_container_width=True):
            deal_profile.status = status
            existing = load_deals(DEALS_FILE)
            # Replace if same id, otherwise append
            ids = [d.id for d in existing]
            if deal_profile.id in ids:
                existing[ids.index(deal_profile.id)] = deal_profile
            else:
                existing.append(deal_profile)
            save_deals(existing, DEALS_FILE)
            mark_profile_mutated()
            st.success("Deal saved.")

    with col_load:
        st.subheader("Saved Deals")
        deals = load_deals(DEALS_FILE)
        if not deals:
            st.info("No saved deals yet.")
        else:
            for d in deals:
                addr = d.property_details.address or d.id[:8]
                if st.button(f"Load: {addr} ({d.status})", key=f"load_{d.id}", use_container_width=True):
                    st.session_state["deal_profile"] = d
                    mark_profile_mutated()
                    st.rerun()
