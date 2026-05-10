import streamlit as st

from src.logic.calculations import refresh_deal_calculations
from src.logic.state import _sync_draft_to_profile, initialize_session_state
from src.models import DealProfile


def render_live_verdict_preview(deal: DealProfile):
    """Displays a compact, live-updating preview of the deal verdict in the sidebar."""
    if not deal.verdict_outputs:
        st.info("Enter deal info to see a live verdict.")
        return

    verdict = deal.verdict_outputs.final_verdict
    cash_flow = deal.verdict_outputs.cash_flow_monthly

    if verdict == "Pass":
        icon, color = "✅", "green"
    elif verdict == "Caution":
        icon, color = "⚠️", "orange"
    else:
        icon, color = "❌", "red"

    st.subheader(f"Live Verdict: :{color}[{verdict} {icon}]")
    st.metric(
        label="Projected Monthly Cash Flow",
        value=f"${cash_flow:,.0f}",
        help="Based on current inputs.",
    )
    st.divider()


def render_step_property():
    st.subheader("Step 1: Property Details")
    st.number_input(
        "Purchase Price ($)",
        key="draft_purchase_price",
        min_value=0,
        step=5000,
        format="%d",
        help="The total purchase price of the property.",
    )


def render_step_rent():
    st.subheader("Step 2: Projected Rent")
    st.number_input(
        "Projected Monthly Gross Rent ($)",
        key="draft_projected_monthly_rent",
        min_value=0,
        step=50,
        format="%d",
        help="The estimated total monthly rent you expect to collect.",
    )


def render_step_financing():
    st.subheader("Step 3: Financing Details")
    st.slider(
        "Down Payment",
        key="draft_down_payment_percent",
        min_value=0.0,
        max_value=1.0,
        step=0.01,
        format="%.0f%%",
    )
    st.slider(
        "Interest Rate",
        key="draft_interest_rate",
        min_value=0.0,
        max_value=0.15,
        step=0.001,
        format="%.2f%%",
    )
    st.number_input(
        "Loan Term (Years)", key="draft_loan_term_years", min_value=1, max_value=40, step=1
    )


def render_step_expenses():
    st.subheader("Step 4: Estimated Expenses")
    st.number_input(
        "Total Monthly Expenses ($)",
        key="draft_total_monthly_expenses",
        min_value=0,
        step=25,
        format="%d",
        help="Sum of all recurring monthly expenses (taxes, insurance, maintenance, etc.).",
    )


def render_step_verdict():
    st.subheader("Final Verdict")
    deal = st.session_state.deal_profile

    if not deal.verdict_outputs:
        st.warning("Could not calculate a verdict. Please check your inputs.")
        return

    verdict = deal.verdict_outputs.final_verdict
    cash_flow = deal.verdict_outputs.cash_flow_monthly

    if verdict == "Pass":
        st.success(f"## ✅ Pass: This deal looks promising!")
        st.balloons()
    elif verdict == "Caution":
        st.warning(f"## ⚠️ Caution: This deal is marginal.")
    else:
        st.error(f"## ❌ Fail: This deal does not meet basic cash flow criteria.")

    st.metric("Projected Monthly Cash Flow", f"${cash_flow:,.2f}")


def render_navigation(max_steps: int):
    step = st.session_state.wizard_step
    is_final_step = step == max_steps - 1

    if is_final_step:
        if st.button("Start Over", use_container_width=True, type="primary"):
            st.session_state.wizard_step = 0
            st.rerun()
        return

    col1, col2 = st.columns(2)
    if step > 0:
        col1.button("⬅️ Back", on_click=lambda: st.session_state.update(wizard_step=st.session_state.wizard_step - 1), use_container_width=True)
    
    col2.button("Next ➡️", on_click=lambda: st.session_state.update(wizard_step=st.session_state.wizard_step + 1), use_container_width=True, type="primary")


def render():
    st.title("Deal Verdict Wizard")

    initialize_session_state()
    _sync_draft_to_profile(st.session_state.deal_profile)
    refresh_deal_calculations(st.session_state.deal_profile)

    steps = [render_step_property, render_step_rent, render_step_financing, render_step_expenses, render_step_verdict]
    
    progress_value = (st.session_state.wizard_step) / (len(steps) - 1)
    st.progress(progress_value, text=f"Step {st.session_state.wizard_step + 1}")

    with st.sidebar:
        if st.session_state.wizard_step < len(steps) - 1:
            render_live_verdict_preview(st.session_state.deal_profile)

    steps[st.session_state.wizard_step]()
    render_navigation(len(steps))