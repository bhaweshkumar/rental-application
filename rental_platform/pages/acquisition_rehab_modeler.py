"""Acquisition & Rehab Modeler page."""
import streamlit as st

from rental_platform.constants import REHAB_COSTS_PER_SQFT
from rental_platform.services.rehab_service import calculate_rehab_costs
from rental_platform.services.brrrr_service import calculate_brrrr_metrics
from rental_platform.services.verdict_service import refresh_deal_calculations
from rental_platform.session import mark_profile_mutated
from rental_platform.utils import get_safe_index


REHAB_LEVEL_OPTIONS = list(REHAB_COSTS_PER_SQFT.keys())


def show_acquisition_rehab_modeler() -> None:
    st.header("Step 2: Acquisition & Rehab Modeler")
    st.markdown(
        "Model the full cost of acquiring and improving the property. "
        "This includes the purchase price, rehab costs, and contingency buffer."
    )
    st.caption("Changes save automatically and refresh the shared deal state.")

    deal_profile = st.session_state["deal_profile"]
    acq = deal_profile.acquisition_details
    prop = deal_profile.property_details

    with st.container(border=True):
        st.subheader("Acquisition")
        purchase_price = st.number_input("Purchase Price ($)", min_value=0,
            value=acq.purchase_price, step=5000,
            help="The total purchase price of the property.")
        arv = st.number_input("After Repair Value (ARV) ($)", min_value=0,
            value=acq.arv, step=5000,
            help="Estimated value of the property after all repairs are complete.")

    with st.container(border=True):
        st.subheader("Rehab Estimation")
        rehab_level = st.selectbox("Rehab Level", options=REHAB_LEVEL_OPTIONS,
            index=get_safe_index(REHAB_LEVEL_OPTIONS, acq.rehab_level))
        contingency_pct = st.slider("Contingency (%)", 0, 30, acq.contingency_pct, 5,
            help="Buffer added to base rehab cost for unexpected expenses.")

        base_cost, contingency_amt, total_budget = calculate_rehab_costs(
            prop.sq_ft, rehab_level, contingency_pct
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Base Rehab Cost", f"${base_cost:,.0f}")
        c2.metric("Contingency", f"${contingency_amt:,.0f}")
        c3.metric("Total Rehab Budget", f"${total_budget:,.0f}")

    with st.container(border=True):
        st.subheader("BRRRR Analysis")
        refi_ltv = st.slider("Refi LTV (%)", 50, 80, 75, 5,
            help="Expected LTV on the cash-out refinance after rehab.")

        brrrr = calculate_brrrr_metrics(purchase_price, total_budget, arv, refi_ltv)
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("All-In Cost", f"${brrrr.all_in_cost:,.0f}")
        b2.metric("Equity Captured", f"${brrrr.equity_capture:,.0f}")
        b3.metric("Refi Loan Amount", f"${brrrr.refi_loan_amount:,.0f}")
        b4.metric("Cash Out", f"${brrrr.cash_out_proceeds:,.0f}",
            delta="Positive = money back" if brrrr.cash_out_proceeds > 0 else "Negative = money left in")

    # Persist to canonical profile
    acq.purchase_price = purchase_price
    acq.arv = arv
    acq.rehab_level = rehab_level
    acq.rehab_cost_per_sqft = float(REHAB_COSTS_PER_SQFT.get(rehab_level, 0))
    acq.base_rehab_cost = base_cost
    acq.contingency_pct = contingency_pct
    acq.total_rehab_budget = total_budget
    refresh_deal_calculations(deal_profile)
    mark_profile_mutated()

    st.success("Acquisition & Rehab model updated.")
    st.info("Next, proceed to **Capital Markets** to model your financing.")
