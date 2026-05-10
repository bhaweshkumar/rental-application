"""Deal Summary Report page."""
import streamlit as st

from rental_platform.pages.components.verdict_summary import render_verdict_summary
from rental_platform.services.verdict_service import refresh_deal_calculations


def show_deal_summary_report() -> None:
    st.header("Deal Summary Report")
    st.markdown(
        "A consolidated view of the full deal analysis — property, financing, "
        "underwriting, verdict, and projections."
    )

    deal_profile = st.session_state["deal_profile"]
    refresh_deal_calculations(deal_profile)

    prop = deal_profile.property_details
    acq = deal_profile.acquisition_details
    cap = deal_profile.capital_markets_details

    if not prop.address and acq.purchase_price <= 0:
        st.info("Enter deal data using the pages in the Deal Analysis section, then return here for the summary.")
        return

    with st.container(border=True):
        st.subheader("Property")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Address", prop.address or "—")
        c2.metric("Asset Type", prop.asset_type)
        c3.metric("State", prop.state or "—")
        c4.metric("Purchase Price", f"${acq.purchase_price:,.0f}")

    with st.container(border=True):
        st.subheader("Financing")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Loan Type", cap.loan_type)
        c2.metric("Loan Amount", f"${cap.loan_amount:,.0f}")
        c3.metric("Monthly P&I", f"${cap.monthly_payment:,.0f}")
        c4.metric("Cash to Close", f"${cap.down_payment + cap.closing_costs:,.0f}")

    with st.container(border=True):
        render_verdict_summary(deal_profile, title="Verdict Summary")
