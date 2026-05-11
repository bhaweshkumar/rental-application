"""
Deal Verdict Wizard — guided 5-step passive rental analysis workflow.

Session management:
  - Draft inputs are stored in st.session_state with the "deal_wizard_draft_" prefix.
  - On every render, draft values are written back to the canonical deal_profile and
    calculations are refreshed (draft → profile → recalculate).
  - If any other page has mutated the canonical profile (profile_version changed),
    the wizard RESEEDS all draft values from the profile before rendering controls.
    This prevents stale wizard inputs from overwriting newer data entered elsewhere.
"""
import copy
from typing import Callable, Dict, Optional

import streamlit as st

from rental_platform.constants import ASSET_TYPE_OPTIONS, US_STATES
from rental_platform.pages.components.verdict_summary import render_verdict_summary
from rental_platform.services.verdict_service import (
    get_missing_fields_for_step,
    refresh_deal_calculations,
)
from rental_platform.session import (
    WIZARD_FEEDBACK_KEY,
    WIZARD_STEP_KEY,
    draft_key,
    mark_wizard_synced,
    reset_deal,
    should_reseed_wizard_drafts,
)
from rental_platform.utils import coerce_float, coerce_int, get_safe_index

# ── wizard configuration ─────────────────────────────────────────────────
WIZARD_STEPS = [
    ("property", "Property"),
    ("rent", "Rent"),
    ("financing", "Financing"),
    ("expenses", "Expenses"),
    ("verdict", "Verdict"),
]
STEP_LABELS = {key: label for key, label in WIZARD_STEPS}
FINANCING_MODE_OPTIONS = ["LTV %", "Down Payment $"]
LOAN_TYPE_OPTIONS = ["DSCR", "Conventional", "FHA", "Creative"]
HOA_REQUIRED_ASSET_TYPES = {"Condo", "Townhome"}

FIELD_LABELS = {
    "address": "Property Address",
    "asset_type": "Asset Type",
    "sq_ft": "Square Footage",
    "year_built": "Year Built",
    "state": "State",
    "purchase_price": "Asking Price",
    "monthly_rent": "Expected Monthly Rent",
    "monthly_other_income": "Other Monthly Income",
    "vacancy_pct": "Vacancy Rate (%)",
    "loan_type": "Loan Type",
    "wizard_financing_mode": "Financing Input Mode",
    "ltv_pct": "Loan-to-Value (LTV) %",
    "down_payment": "Down Payment ($)",
    "interest_rate_pct": "Interest Rate (%)",
    "term_years": "Loan Term (Years)",
    "closing_costs_pct": "Closing Costs (%)",
    "annual_property_taxes": "Annual Property Taxes",
    "annual_insurance": "Annual Insurance",
    "monthly_hoa": "Monthly HOA",
    "monthly_property_management": "Monthly Property Management",
    "monthly_maintenance_reserve": "Monthly Maintenance / Reserve",
    "monthly_owner_paid_utilities": "Monthly Owner-Paid Utilities",
    "monthly_other_expenses": "Other Monthly Expenses",
    "rent_ready_repairs": "One-Time Rent-Ready Repairs",
}

STEP_FIELDS = {
    "property": ["address", "asset_type", "sq_ft", "year_built", "state", "purchase_price"],
    "rent": ["monthly_rent", "monthly_other_income", "vacancy_pct"],
    "financing": [
        "loan_type", "wizard_financing_mode", "ltv_pct", "down_payment",
        "interest_rate_pct", "term_years", "closing_costs_pct",
    ],
    "expenses": [
        "annual_property_taxes", "annual_insurance", "monthly_hoa",
        "monthly_property_management", "monthly_maintenance_reserve",
        "monthly_owner_paid_utilities", "monthly_other_expenses", "rent_ready_repairs",
    ],
}


# ── feedback helpers ─────────────────────────────────────────────────────
def _feedback_state() -> Dict[str, Dict[str, str]]:
    return st.session_state.setdefault(WIZARD_FEEDBACK_KEY, {})


def _set_step_feedback(step_key: str, level: str, message: str) -> None:
    _feedback_state()[step_key] = {"level": level, "message": message}


def _clear_step_feedback(step_key: str) -> None:
    _feedback_state().pop(step_key, None)


def _get_step_feedback(step_key: str) -> Dict[str, str]:
    return _feedback_state().get(step_key, {})


def _set_step_error(step_key: str, message: str) -> None:
    if message:
        _set_step_feedback(step_key, "error", message)
    else:
        _clear_step_feedback(step_key)


def _show_feedback(step_key: str) -> None:
    feedback = _get_step_feedback(step_key)
    if not feedback:
        return
    level = feedback.get("level", "info")
    message = feedback.get("message", "")
    if level == "warning":
        st.warning(message)
    elif level == "success":
        st.success(message)
    else:
        st.error(message)


# ── navigation helpers ───────────────────────────────────────────────────
def _go_to_step(step_index: int) -> None:
    st.session_state[WIZARD_STEP_KEY] = max(0, min(step_index, len(WIZARD_STEPS) - 1))


def _go_to_next_step() -> None:
    _go_to_step(st.session_state[WIZARD_STEP_KEY] + 1)


def _go_to_previous_step() -> None:
    _go_to_step(st.session_state[WIZARD_STEP_KEY] - 1)


def _show_step_actions(previous_label: Optional[str], submit_label: str) -> Optional[str]:
    nav_col1, nav_col2 = st.columns(2)
    if previous_label:
        if nav_col1.button(previous_label, use_container_width=True):
            return "previous"
    if nav_col2.button(submit_label, use_container_width=True):
        return "next"
    return None


# ── draft seed / sync ────────────────────────────────────────────────────
def _seed_draft_values(deal_profile) -> Dict[str, object]:
    """Reads the canonical profile and returns a flat dict of draft values."""
    prop = deal_profile.property_details
    acq = deal_profile.acquisition_details
    vi = deal_profile.verdict_inputs
    cap = deal_profile.capital_markets_details
    exp = deal_profile.expense_line_items
    return {
        "address": prop.address,
        "asset_type": prop.asset_type,
        "sq_ft": coerce_int(prop.sq_ft, minimum=0),
        "year_built": coerce_int(prop.year_built, minimum=1800, maximum=2100),
        "state": prop.state,
        "purchase_price": coerce_int(acq.purchase_price, minimum=0),
        "monthly_rent": coerce_float(vi.monthly_rent, minimum=0.0),
        "monthly_other_income": coerce_float(vi.monthly_other_income, minimum=0.0),
        "vacancy_pct": coerce_int(vi.vacancy_pct, minimum=0, maximum=20),
        "loan_type": cap.loan_type,
        "wizard_financing_mode": deal_profile.other_details.get("wizard_financing_mode", "LTV %"),
        "ltv_pct": coerce_int(cap.ltv_pct, minimum=50, maximum=97),
        "down_payment": coerce_float(cap.down_payment, minimum=0.0),
        "interest_rate_pct": coerce_float(cap.interest_rate_pct, minimum=0.0, maximum=20.0),
        "term_years": coerce_int(cap.term_years, minimum=15, maximum=30),
        "closing_costs_pct": coerce_int(cap.closing_costs_pct, minimum=0, maximum=7),
        "annual_property_taxes": coerce_float(exp.annual_property_taxes, minimum=0.0),
        "annual_insurance": coerce_float(exp.annual_insurance, minimum=0.0),
        "monthly_hoa": coerce_float(exp.monthly_hoa, minimum=0.0),
        "monthly_property_management": coerce_float(exp.monthly_property_management, minimum=0.0),
        "monthly_maintenance_reserve": coerce_float(exp.monthly_maintenance_reserve, minimum=0.0),
        "monthly_owner_paid_utilities": coerce_float(exp.monthly_owner_paid_utilities, minimum=0.0),
        "monthly_other_expenses": coerce_float(exp.monthly_other_expenses, minimum=0.0),
        "rent_ready_repairs": coerce_float(vi.rent_ready_repairs, minimum=0.0),
    }


def _ensure_wizard_drafts(deal_profile) -> None:
    """
    Reseeds wizard draft keys from the canonical profile when needed.

    Reseeding occurs when:
      - An external page incremented profile_version (external mutation detected), OR
      - This is the first render (version mismatch on initialisation), OR
      - The deal id changed (new deal or reset).

    This is the core fix: stale wizard drafts can no longer overwrite data
    entered on other pages of the application.
    """
    if should_reseed_wizard_drafts():
        for field_name, value in _seed_draft_values(deal_profile).items():
            st.session_state[draft_key(field_name)] = value
        st.session_state[WIZARD_FEEDBACK_KEY] = {}
        mark_wizard_synced()


def _write_field_to_profile(field_name: str, deal_profile) -> None:
    """Reads a single draft key from session_state and writes it into deal_profile.

    Shared by _sync_draft_to_profile (batch safety net on every render) and
    _on_field_change (per-widget immediate commit). If the draft key is absent
    from session_state the function is a no-op — safe to call unconditionally.
    """
    ss = st.session_state
    dk = draft_key(field_name)
    if dk not in ss:
        return
    v = ss[dk]
    prop = deal_profile.property_details
    acq = deal_profile.acquisition_details
    vi = deal_profile.verdict_inputs
    cap = deal_profile.capital_markets_details
    exp = deal_profile.expense_line_items

    if field_name == "address":
        prop.address = str(v or "").strip()
    elif field_name == "asset_type":
        prop.asset_type = v
    elif field_name == "sq_ft":
        prop.sq_ft = coerce_int(v, minimum=0)
    elif field_name == "year_built":
        prop.year_built = coerce_int(v, minimum=1800, maximum=2100)
    elif field_name == "state":
        prop.state = v
    elif field_name == "purchase_price":
        acq.purchase_price = coerce_int(v, minimum=0)
    elif field_name == "monthly_rent":
        vi.monthly_rent = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_other_income":
        vi.monthly_other_income = coerce_float(v, minimum=0.0)
    elif field_name == "vacancy_pct":
        vi.vacancy_pct = coerce_int(v, minimum=0, maximum=20)
    elif field_name == "rent_ready_repairs":
        vi.rent_ready_repairs = coerce_float(v, minimum=0.0)
    elif field_name == "wizard_financing_mode":
        deal_profile.other_details["wizard_financing_mode"] = v
    elif field_name == "loan_type":
        cap.loan_type = v
    elif field_name == "ltv_pct":
        cap.ltv_pct = coerce_int(v, minimum=50, maximum=97)
    elif field_name == "down_payment":
        cap.down_payment = coerce_float(v, minimum=0.0)
    elif field_name == "interest_rate_pct":
        cap.interest_rate_pct = coerce_float(v, minimum=0.0, maximum=20.0)
    elif field_name == "term_years":
        cap.term_years = coerce_int(v, minimum=15, maximum=30)
    elif field_name == "closing_costs_pct":
        cap.closing_costs_pct = coerce_int(v, minimum=0, maximum=7)
    elif field_name == "annual_property_taxes":
        exp.annual_property_taxes = coerce_float(v, minimum=0.0)
    elif field_name == "annual_insurance":
        exp.annual_insurance = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_hoa":
        exp.monthly_hoa = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_property_management":
        exp.monthly_property_management = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_maintenance_reserve":
        exp.monthly_maintenance_reserve = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_owner_paid_utilities":
        exp.monthly_owner_paid_utilities = coerce_float(v, minimum=0.0)
    elif field_name == "monthly_other_expenses":
        exp.monthly_other_expenses = coerce_float(v, minimum=0.0)


def _on_field_change(field_name: str) -> None:
    """on_change callback: immediately commits the changed widget field into deal_profile.

    Streamlit calls this before the next script rerun so the profile is updated
    atomically with the widget interaction. This is the primary persistence mechanism
    — on_change fires even when the user jumps tabs before the next render, ensuring
    Rent, Financing, and Expenses values survive step navigation.
    """
    deal_profile = st.session_state["deal_profile"]
    _write_field_to_profile(field_name, deal_profile)
    refresh_deal_calculations(deal_profile)


def _sync_draft_to_profile(deal_profile) -> None:
    """Batch-writes all present draft values into the canonical deal_profile.

    Defensive safety net called at the top of every render. Keys absent from
    session_state are silently skipped via _write_field_to_profile's no-op guard,
    so the profile is never corrupted with minimum placeholder values. With
    on_change callbacks covering per-field commits, this function's role is
    secondary — it catches any edge case where on_change did not fire.
    """
    for field_name in _seed_draft_values(deal_profile):
        _write_field_to_profile(field_name, deal_profile)


def _restore_missing_draft_keys(deal_profile) -> None:
    """Re-populates draft keys that Streamlit's widget-state cleanup removed.

    Must be called AFTER _sync_draft_to_profile so the profile already holds the
    latest committed values. Only keys absent from session_state are written —
    present keys (i.e. the current step's in-progress edits) are left untouched.
    """
    for field_name, value in _seed_draft_values(deal_profile).items():
        if draft_key(field_name) not in st.session_state:
            st.session_state[draft_key(field_name)] = value


def _refresh_wizard_profile(deal_profile) -> None:
    """Syncs drafts → profile, restores any cleaned-up draft keys, then recalculates.

    Call order matters:
      1. _sync_draft_to_profile   — flush present draft keys into the profile.
      2. _restore_missing_draft_keys — refill absent draft keys from the profile so
         widget state cleaned up by Streamlit (keys for non-rendered steps) is
         automatically recovered before the current step renders.
      3. refresh_deal_calculations — recompute all derived metrics.
    """
    _sync_draft_to_profile(deal_profile)
    _restore_missing_draft_keys(deal_profile)
    refresh_deal_calculations(deal_profile)


# ── validation ───────────────────────────────────────────────────────────
def _format_missing_fields(missing_fields) -> str:
    return ", ".join(
        FIELD_LABELS.get(f, f.replace("_", " ").title()) for f in missing_fields
    )


def _validate_current_step(step_key: str, deal_profile) -> bool:
    missing = get_missing_fields_for_step(step_key, deal_profile)
    if missing:
        _set_step_feedback(
            step_key,
            "warning",
            f"Complete the required fields before continuing: {_format_missing_fields(missing)}",
        )
        return False
    _clear_step_feedback(step_key)
    return True


def _save_step(step_key: str, deal_profile, *, go_next: bool) -> bool:
    if not _validate_current_step(step_key, deal_profile):
        return False
    if go_next:
        _go_to_next_step()
    return True


# ── widget helpers ───────────────────────────────────────────────────────
# All helpers pass value=st.session_state.get(dk, minimum) together with
# key=dk. _restore_missing_draft_keys pre-populates every draft key from the
# canonical profile before any widget renders, so value== and the stored key
# always agree. This prevents Streamlit from reinitialising a "returning"
# widget (one absent in the previous step) to min_value, which would otherwise
# trigger on_change with an incorrect 0 and corrupt the profile.

def _draft_select(label: str, field_name: str, options, *, help_text: Optional[str] = None) -> None:
    current_value = st.session_state.get(draft_key(field_name), options[0] if options else "")
    st.selectbox(
        label,
        options=options,
        index=get_safe_index(options, current_value),
        key=draft_key(field_name),
        help=help_text,
        on_change=_on_field_change,
        args=(field_name,),
    )


def _draft_text(label: str, field_name: str) -> None:
    dk = draft_key(field_name)
    st.text_input(
        label,
        value=st.session_state.get(dk, ""),
        key=dk,
        on_change=_on_field_change,
        args=(field_name,),
    )


def _draft_number_input(
    label: str,
    field_name: str,
    *,
    minimum,
    maximum=None,
    step=1,
    help_text: Optional[str] = None,
) -> None:
    dk = draft_key(field_name)
    kwargs = {
        "label": label,
        "min_value": minimum,
        "value": st.session_state.get(dk, minimum),
        "step": step,
        "key": dk,
        "help": help_text,
        "on_change": _on_field_change,
        "args": (field_name,),
    }
    if maximum is not None:
        kwargs["max_value"] = maximum
    st.number_input(**kwargs)


def _draft_slider(
    label: str,
    field_name: str,
    *,
    minimum,
    maximum,
    step,
    help_text: Optional[str] = None,
) -> None:
    dk = draft_key(field_name)
    st.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        value=st.session_state.get(dk, minimum),
        step=step,
        key=dk,
        help=help_text,
        on_change=_on_field_change,
        args=(field_name,),
    )


# ── step renderers ───────────────────────────────────────────────────────
def _show_step_header(step_label: str, step_index: int) -> None:
    st.header("Deal Verdict Wizard")
    st.caption(
        "A guided workflow for deciding whether a property is priced well enough "
        "to work as a passive long-term rental."
    )
    st.progress((step_index + 1) / len(WIZARD_STEPS))
    labels = " -> ".join(f"{i + 1}. {lbl}" for i, (_, lbl) in enumerate(WIZARD_STEPS))
    st.caption(labels)
    st.subheader(f"Step {step_index + 1}: {step_label}")


def _render_step_navigation() -> None:
    columns = st.columns(len(WIZARD_STEPS))
    current_step = st.session_state[WIZARD_STEP_KEY]
    for index, (step_key, label) in enumerate(WIZARD_STEPS):
        button_type = "primary" if current_step == index else "secondary"
        if columns[index].button(label, key=f"wizard_nav_{step_key}", type=button_type, use_container_width=True):
            _go_to_step(index)
            st.rerun()


def _render_missing_inputs_summary(deal_profile) -> None:
    summary: Dict[str, list] = {}
    for step_key, step_label in WIZARD_STEPS:
        if step_key == "verdict":
            continue
        missing = get_missing_fields_for_step(step_key, deal_profile)
        if missing:
            summary[step_label] = [
                FIELD_LABELS.get(f, f.replace("_", " ").title()) for f in missing
            ]
    if not summary:
        return
    st.warning("This verdict is incomplete until you finish the missing inputs below.")
    for step_label, missing_fields in summary.items():
        st.write(f"- {step_label}: {', '.join(missing_fields)}")


def _render_live_verdict_preview(deal_profile) -> None:
    outputs = deal_profile.verdict_outputs
    st.markdown("##### Live Verdict Preview")
    if outputs.verdict_status == "Pass":
        st.success("Pass based on the current inputs.")
    elif outputs.verdict_status == "Caution":
        st.warning("Caution based on the current inputs.")
    else:
        st.error("Fail or incomplete based on the current inputs.")

    preview_cols = st.columns(4)
    preview_cols[0].metric("Monthly Cash Flow", f"${outputs.monthly_cash_flow:,.0f}")
    preview_cols[1].metric("DSCR", f"{outputs.dscr:.2f}")
    preview_cols[2].metric("Cash Required", f"${outputs.total_cash_required:,.0f}")
    preview_cols[3].metric("Cap Rate", f"{outputs.cap_rate:.2f}%")

    if outputs.verdict_reasons:
        st.caption(" | ".join(outputs.verdict_reasons))


def _render_property_step(deal_profile) -> None:
    _draft_text("Property Address", "address")
    _draft_select("Asset Type", "asset_type", ASSET_TYPE_OPTIONS)
    col1, col2 = st.columns(2)
    with col1:
        _draft_number_input("Square Footage", "sq_ft", minimum=0, step=50)
    with col2:
        _draft_number_input("Year Built", "year_built", minimum=1800, maximum=2100, step=1)
    _draft_select("State", "state", US_STATES)
    _draft_number_input("Asking Price", "purchase_price", minimum=0, step=5000)

    action = _show_step_actions(None, "Continue to Rent")
    if action == "next" and _save_step("property", deal_profile, go_next=True):
        st.rerun()


def _render_rent_step(deal_profile) -> None:
    _draft_number_input("Expected Monthly Rent", "monthly_rent", minimum=0.0, step=100.0)
    _draft_number_input(
        "Other Monthly Income", "monthly_other_income", minimum=0.0, step=25.0,
        help_text="Parking, pet rent, laundry, or other recurring monthly income.",
    )
    _draft_slider("Vacancy Rate (%)", "vacancy_pct", minimum=0, maximum=20, step=1)

    action = _show_step_actions("Back to Property", "Continue to Financing")
    if action == "previous":
        _go_to_previous_step()
        st.rerun()
    if action == "next" and _save_step("rent", deal_profile, go_next=True):
        st.rerun()


def _render_financing_step(deal_profile) -> None:
    if coerce_int(st.session_state.get(draft_key("purchase_price")), minimum=0) <= 0:
        st.warning("Set the asking price first in Step 1.")
        return

    capital = deal_profile.capital_markets_details
    _draft_select("Loan Type", "loan_type", LOAN_TYPE_OPTIONS)
    _draft_select("Financing Input Mode", "wizard_financing_mode", FINANCING_MODE_OPTIONS)

    financing_mode = st.session_state.get(draft_key("wizard_financing_mode"), "LTV %")
    purchase_price = float(coerce_int(st.session_state.get(draft_key("purchase_price")), minimum=0))

    col1, col2, col3 = st.columns(3)
    with col1:
        if financing_mode == "LTV %":
            _draft_slider("Loan-to-Value (LTV) %", "ltv_pct", minimum=50, maximum=97, step=1)
        else:
            _draft_number_input(
                "Down Payment ($)", "down_payment",
                minimum=0.0, maximum=float(purchase_price), step=5000.0,
            )
        _draft_number_input("Interest Rate (%)", "interest_rate_pct", minimum=0.0, maximum=20.0, step=0.125)
    with col2:
        _draft_select("Loan Term (Years)", "term_years", [30, 25, 20, 15])
        _draft_slider("Closing Costs (%)", "closing_costs_pct", minimum=0, maximum=7, step=1)
    with col3:
        st.metric("Loan Amount", f"${capital.loan_amount:,.0f}")
        st.metric("Down Payment", f"${capital.down_payment:,.0f}")
        st.metric("Implied LTV", f"{capital.ltv_pct}%")

    st.info(
        f"Estimated monthly P&I: ${capital.monthly_payment:,.0f}. "
        f"Estimated cash to close (excl. rent-ready repairs): "
        f"${capital.down_payment + capital.closing_costs:,.0f}."
    )

    action = _show_step_actions("Back to Rent", "Continue to Expenses")
    if action == "previous":
        _go_to_previous_step()
        st.rerun()
    if action == "next" and _save_step("financing", deal_profile, go_next=True):
        st.rerun()


def _render_expenses_step(deal_profile) -> None:
    asset_type = st.session_state.get(draft_key("asset_type"), "")
    st.markdown("Enter the recurring and one-time costs that affect profitability and the final verdict.")
    if asset_type in HOA_REQUIRED_ASSET_TYPES:
        st.info(f"{asset_type} deals require an HOA amount because it affects profitability directly.")

    col1, col2 = st.columns(2)
    with col1:
        _draft_number_input("Annual Property Taxes", "annual_property_taxes", minimum=0.0, step=250.0)
        _draft_number_input("Annual Insurance", "annual_insurance", minimum=0.0, step=100.0)
        _draft_number_input("Monthly HOA", "monthly_hoa", minimum=0.0, step=25.0)
        _draft_number_input("Monthly Property Management", "monthly_property_management", minimum=0.0, step=25.0)
    with col2:
        _draft_number_input("Monthly Maintenance / Reserve", "monthly_maintenance_reserve", minimum=0.0, step=25.0)
        _draft_number_input("Monthly Owner-Paid Utilities", "monthly_owner_paid_utilities", minimum=0.0, step=25.0)
        _draft_number_input("Other Monthly Expenses", "monthly_other_expenses", minimum=0.0, step=25.0)
        _draft_number_input(
            "One-Time Rent-Ready Repairs", "rent_ready_repairs", minimum=0.0, step=500.0,
            help_text="Use for small make-ready work. Heavy rehab is handled separately.",
        )

    action = _show_step_actions("Back to Financing", "Continue to Verdict")
    if action == "previous":
        _go_to_previous_step()
        st.rerun()
    if action == "next" and _save_step("expenses", deal_profile, go_next=True):
        st.rerun()


def _render_verdict_step(deal_profile) -> None:
    draft_deal = copy.deepcopy(deal_profile)
    refresh_deal_calculations(draft_deal)

    _render_missing_inputs_summary(draft_deal)
    render_verdict_summary(draft_deal, title="Passive Rental Verdict")

    action_col1, action_col2 = st.columns(2)
    with action_col1:
        if st.button("Back to Expenses", use_container_width=True):
            _go_to_previous_step()
            st.rerun()
    with action_col2:
        if st.button("Start Over", use_container_width=True):
            reset_deal()
            st.rerun()


# ── public entry point ───────────────────────────────────────────────────
def show_deal_verdict_wizard() -> None:
    """Displays the primary guided workflow for single-deal passive rental analysis."""
    deal_profile = st.session_state["deal_profile"]

    # Reseed drafts if another page changed the canonical profile
    _ensure_wizard_drafts(deal_profile)

    # Always sync drafts → profile → recalculate before rendering
    _refresh_wizard_profile(deal_profile)

    step_index = st.session_state[WIZARD_STEP_KEY]
    step_key, step_label = WIZARD_STEPS[step_index]

    _show_step_header(step_label, step_index)
    _render_step_navigation()

    renderers: Dict[str, Callable[[object], None]] = {
        "property": _render_property_step,
        "rent": _render_rent_step,
        "financing": _render_financing_step,
        "expenses": _render_expenses_step,
        "verdict": _render_verdict_step,
    }
    try:
        renderers[step_key](deal_profile)
    except Exception as exc:  # pragma: no cover
        _set_step_error(
            step_key,
            f"Unexpected error on this step. Inputs are preserved. Details: {exc}",
        )

    if step_key != "verdict":
        _render_live_verdict_preview(deal_profile)
    _show_feedback(step_key)
