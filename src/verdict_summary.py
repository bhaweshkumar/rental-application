import streamlit as st

from logic.verdict import apply_verdict_to_underwriting_fields, evaluate_deal_verdict


def render_verdict_summary(deal_profile, *, title: str = "Deal Verdict") -> None:
    """Renders the guided verdict report for a single property."""
    outputs = evaluate_deal_verdict(deal_profile)
    deal_profile.verdict_outputs = outputs
    apply_verdict_to_underwriting_fields(deal_profile)

    status = outputs.verdict_status
    st.subheader(title)

    if status == "Pass":
        st.success("Pass: the property clears the passive rental threshold.")
    elif status == "Caution":
        st.warning("Caution: the property works on paper, but it misses at least one preferred threshold.")
    else:
        st.error("Fail: the property does not currently qualify as a strong passive rental deal.")

    metrics = st.columns(5)
    metrics[0].metric("Monthly Cash Flow", f"${outputs.monthly_cash_flow:,.0f}")
    metrics[1].metric("DSCR", f"{outputs.dscr:.2f}")
    metrics[2].metric("Cap Rate", f"{outputs.cap_rate:.2f}%")
    metrics[3].metric("Cash-on-Cash", f"{outputs.cash_on_cash_return:.2f}%")
    metrics[4].metric("Cash Required", f"${outputs.total_cash_required:,.0f}")

    st.markdown("##### Why This Verdict")
    for reason in outputs.verdict_reasons:
        st.write(f"- {reason}")

    detail_col1, detail_col2, detail_col3 = st.columns(3)
    detail_col1.metric("Effective Gross Income", f"${outputs.effective_gross_income:,.0f}/yr")
    detail_col2.metric("Operating Expenses", f"${outputs.annual_operating_expenses:,.0f}/yr")
    detail_col3.metric("Net Operating Income", f"${outputs.noi:,.0f}/yr")
