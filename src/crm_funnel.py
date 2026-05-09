import streamlit as st
import pandas as pd
from typing import List

try:
    from src.logic.models import DealProfile  # type: ignore
except ImportError:
    from logic.models import DealProfile  # type: ignore

from logic.crm import save_deals, load_deals

DEALS_FILE = "deals.json"

def show_crm_funnel():
    """Displays the UI for Feature 8: Automated Lead Funnel (CRM)."""
    st.header("Feature 8: Automated Lead Funnel (CRM)")
    st.markdown("Manage your pipeline of potential investment properties. Save, load, and compare deals.")

    all_deals: List[DealProfile] = load_deals(DEALS_FILE)
    active_deal = st.session_state.deal_profile

    # --- Actions for the current deal in session ---
    st.subheader("Active Deal Actions", divider="blue")
    st.text(f"Active Deal in Session: {active_deal.property_details.address or 'Untitled Deal'}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Active Deal to CRM"):
            deal_exists = any(d.id == active_deal.id for d in all_deals)
            if deal_exists:
                all_deals = [active_deal if d.id == active_deal.id else d for d in all_deals]
            else:
                all_deals.append(active_deal)

            save_deals(all_deals, DEALS_FILE)
            st.success(f"Deal '{active_deal.property_details.address}' saved to CRM.")
            st.rerun()

    with col2:
        if st.button("➕ Create New Blank Deal"):
            st.session_state.deal_profile = DealProfile()
            st.success("New blank deal created. Navigate to other features to add details.")
            st.rerun()

    # --- Display Deal Pipeline ---
    st.subheader("Deal Pipeline", divider="blue")
    if not all_deals:
        st.info("No deals saved in the CRM yet. Save the active deal to get started.")
        return

    deal_data = [
        {
            "Address": d.property_details.address or "Untitled",
            "Status": d.status,
            "Purchase Price": d.acquisition_details.purchase_price,
            "NOI": d.underwriting_outputs.noi,
            "CoC Return": d.underwriting_outputs.cash_on_cash_return,
            "id": d.id,
        }
        for d in all_deals
    ]
    df = pd.DataFrame(deal_data)
    st.dataframe(
        df.drop(columns=['id']),
        column_config={
            "Purchase Price": st.column_config.NumberColumn(format="$%d"),
            "NOI": st.column_config.NumberColumn(format="$%d/yr"),
            "CoC Return": st.column_config.NumberColumn(format="%.2f%%"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- Deal Management ---
    st.markdown("#### Manage Deals")
    deal_options = {f"{d.property_details.address or 'Untitled'} (ID: {d.id[:8]})": d.id for d in all_deals}
    selected_option = st.selectbox("Select a deal to manage:", options=[""] + list(deal_options.keys()))

    if selected_option:
        selected_id = deal_options[selected_option]
        selected_deal_index = next((i for i, deal in enumerate(all_deals) if deal.id == selected_id), None)

        if selected_deal_index is not None:
            scol1, scol2, scol3 = st.columns([2, 1, 1])
            with scol1:
                # Status editor
                current_status = all_deals[selected_deal_index].status
                status_options = ["Analysis", "Under Contract", "Rejected", "Closed"]
                new_status = st.selectbox("Update Status:", options=status_options, index=status_options.index(current_status), key=f"status_{selected_id}")
                if new_status != current_status:
                    all_deals[selected_deal_index].status = new_status
                    save_deals(all_deals, DEALS_FILE)
                    st.success(f"Status for '{selected_option}' updated to '{new_status}'.")
                    st.rerun()
            with scol2:
                if st.button("📂 Load to Session", key=f"load_{selected_id}", use_container_width=True):
                    st.session_state.deal_profile = all_deals[selected_deal_index]
                    st.success(f"Loaded '{selected_option}' into the active session.")
                    st.rerun()
            with scol3:
                if st.button("❌ Delete", type="primary", key=f"delete_{selected_id}", use_container_width=True):
                    all_deals.pop(selected_deal_index)
                    save_deals(all_deals, DEALS_FILE)
                    st.warning(f"Deleted '{selected_option}'.")
                    if active_deal.id == selected_id:
                        st.session_state.deal_profile = DealProfile()
                    st.rerun()
