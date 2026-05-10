"""
Debug helper for wizard state persistence issues.
Run the app and add this to any wizard step to see session state:

    import debug_wizard_state
    debug_wizard_state.show_debug_info()
"""

import streamlit as st


def show_debug_info():
    """Display current wizard session state for debugging."""
    st.sidebar.markdown("### 🔍 Debug Info")
    
    # Show wizard step
    current_step = st.session_state.get("deal_wizard_step", "NOT SET")
    st.sidebar.write(f"**Current Step:** {current_step}")
    
    # Show deal profile ID
    deal_id = st.session_state.get("deal_profile", {})
    if hasattr(deal_id, "id"):
        st.sidebar.write(f"**Deal ID:** {deal_id.id[:8]}...")
    
    # Show draft state ID
    draft_id = st.session_state.get("deal_wizard_draft_deal_id", "NOT SET")
    if draft_id and draft_id != "NOT SET":
        st.sidebar.write(f"**Draft ID:** {draft_id[:8]}...")
    
    # Show key wizard fields
    st.sidebar.markdown("**Draft Values:**")
    draft_fields = {
        "address": st.session_state.get("deal_wizard_draft_address", "NOT SET"),
        "purchase_price": st.session_state.get("deal_wizard_draft_purchase_price", "NOT SET"),
        "monthly_rent": st.session_state.get("deal_wizard_draft_monthly_rent", "NOT SET"),
    }
    
    for field, value in draft_fields.items():
        st.sidebar.write(f"  {field}: `{value}`")
    
    # Count total draft keys
    draft_keys = [k for k in st.session_state.keys() if k.startswith("deal_wizard_draft_")]
    st.sidebar.write(f"**Total draft keys:** {len(draft_keys)}")
