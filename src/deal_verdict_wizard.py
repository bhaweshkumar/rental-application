import copy
from typing import Callable, Dict, Optional

import streamlit as st

from logic.verdict import get_missing_fields_for_step, refresh_deal_calculations
from shared.constants import ASSET_TYPE_OPTIONS, US_STATES
from shared.utils import get_safe_index
from verdict_summary import render_verdict_summary


WIZARD_STEPS = [
    ("property", "Property"),
    ("rent", "Rent"),
    ("financing", "Financing"),
    ("expenses", "Expenses"),
    ("verdict", "Verdict"),
]
STEP_LABELS = {key: label for key, label in WIZARD_STEPS}
DRAFT_PREFIX = "deal_wizard_draft"
FEEDBACK_KEY = "deal_wizard_feedback"
DRAFT_DEAL_ID_KEY = "deal_wizard_draft_deal_id"
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
        "loan_type",
        "wizard_financing_mode",
        "ltv_pct",
        "down_payment",
        "interest_rate_pct",
        "term_years",
        "closing_costs_pct",
    ],
    "expenses": [
        "annual_property_taxes",
        "annual_insurance",
        "monthly_hoa",
        "monthly_property_management",
        "monthly_maintenance_reserve",
        "monthly_owner_paid_utilities",
        "monthly_other_expenses",
        "rent_ready_repairs",
    ],
}


def _coerce_int(value, *, minimum: int = 0, maximum: Optional[int] = None) -> int:
    try:
        coerced = int(float(value))
    except (TypeError, ValueError):
        coerced = minimum
    coerced = max(coerced, minimum)
    if maximum is not None:
        coerced = min(coerced, maximum)
    return coerced


def _coerce_float(value, *, minimum: float = 0.0, maximum: Optional[float] = None) -> float:
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        coerced = minimum
    coerced = max(coerced, minimum)
    if maximum is not None:
        coerced = min(coerced, maximum)
    return coerced


def _draft_key(field_name: str) -> str:
    return f"{DRAFT_PREFIX}_{field_name}"


def _feedback_state() -> Dict[str, Dict[str, str]]:
    return st.session_state.setdefault(FEEDBACK_KEY, {})


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


def _get_step_error(step_key: str) -> str:
    return _get_step_feedback(step_key).get("message", "")


def _go_to_step(step_index: int) -> None:
    st.session_state["deal_wizard_step"] = max(0, min(step_index, len(WIZARD_STEPS) - 1))


def _go_to_next_step() -> None:
    _go_to_step(st.session_state["deal_wizard_step"] + 1)


def _go_to_previous_step() -> None:
    _go_to_step(st.session_state["deal_wizard_step"] - 1)


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


def _show_step_header(step_label: str, step_index: int) -> None:
    st.header("Deal Verdict Wizard")
    st.caption(
        "A guided workflow for deciding whether a property is priced well enough to work as a passive long-term rental."
    )
    st.progress((step_index + 1) / len(WIZARD_STEPS))
    labels = " -> ".join(
        f"{idx + 1}. {label}" for idx, (_, label) in enumerate(WIZARD_STEPS)
    )
    st.caption(labels)
    st.subheader(f"Step {step_index + 1}: {step_label}")


def _render_step_navigation() -> None:
    columns = st.columns(len(WIZARD_STEPS))
    current_step = st.session_state["deal_wizard_step"]
    for index, (step_key, label) in enumerate(WIZARD_STEPS):
        button_type = "primary" if current_step == index else "secondary"
        if columns[index].button(label, key=f"wizard_nav_{step_key}", type=button_type, use_container_width=True):
            _go_to_step(index)
            st.rerun()


def _show_step_actions(previous_label: Optional[str], submit_label: str) -> Optional[str]:
    nav_col1, nav_col2 = st.columns(2)
    if previous_label:
        if nav_col1.button(previous_label, use_container_width=True):
            return "previous"
    if nav_col2.button(submit_label, use_container_width=True):
        return "next"
    return None


def _render_missing_inputs_summary(deal_profile) -> None:
    summary = _get_step_status_summary(deal_profile)
    if not summary:
        return
    st.warning("This verdict is incomplete until you finish the missing inputs below.")
    for step_label, missing_fields in summary.items():
        st.write(f"- {step_label}: {', '.join(missing_fields)}")


def _format_missing_fields(missing_fields) -> str:
    return ", ".join(FIELD_LABELS.get(field, field.replace("_", " ").title()) for field in missing_fields)


def _get_step_status_summary(deal_profile) -> Dict[str, list[str]]:
    summary: Dict[str, list[str]] = {}
    for step_key, step_label in WIZARD_STEPS:
        if step_key == "verdict":
            continue
        missing = get_missing_fields_for_step(step_key, deal_profile)
        if missing:
            summary[step_label] = [
                FIELD_LABELS.get(field, field.replace("_", " ").title()) for field in missing
            ]
    return summary


def _run_step(step_key: str, callback: Callable[[], None]) -> bool:
    try:
        callback()
        return True
    except Exception as exc:  # pragma: no cover - error path depends on Streamlit runtime
        _set_step_error(
            step_key,
            "We hit an unexpected error on this step. Your inputs are still saved in the wizard. "
            f"Please correct the values and try again. Technical details: {exc}",
        )
        return False


def _seed_draft_values(deal_profile) -> Dict[str, object]:
    property_details = deal_profile.property_details
    verdict_inputs = deal_profile.verdict_inputs
    capital_details = deal_profile.capital_markets_details
    expenses = deal_profile.expense_line_items
    acquisition_details = deal_profile.acquisition_details

    return {
        "address": property_details.address,
        "asset_type": property_details.asset_type,
        "sq_ft": _coerce_int(property_details.sq_ft, minimum=0),
        "year_built": _coerce_int(property_details.year_built, minimum=1800, maximum=2100),
        "state": property_details.state,
        "purchase_price": _coerce_int(acquisition_details.purchase_price, minimum=0),
        "monthly_rent": _coerce_float(verdict_inputs.monthly_rent, minimum=0.0),
        "monthly_other_income": _coerce_float(verdict_inputs.monthly_other_income, minimum=0.0),
        "vacancy_pct": _coerce_int(verdict_inputs.vacancy_pct, minimum=0, maximum=20),
        "loan_type": capital_details.loan_type,
        "wizard_financing_mode": deal_profile.other_details.get("wizard_financing_mode", "LTV %"),
        "ltv_pct": _coerce_int(capital_details.ltv_pct, minimum=50, maximum=97),
        "down_payment": _coerce_float(capital_details.down_payment, minimum=0.0),
        "interest_rate_pct": _coerce_float(capital_details.interest_rate_pct, minimum=0.0, maximum=20.0),
        "term_years": _coerce_int(capital_details.term_years, minimum=15, maximum=30),
        "closing_costs_pct": _coerce_int(capital_details.closing_costs_pct, minimum=0, maximum=7),
        "annual_property_taxes": _coerce_float(expenses.annual_property_taxes, minimum=0.0),
        "annual_insurance": _coerce_float(expenses.annual_insurance, minimum=0.0),
        "monthly_hoa": _coerce_float(expenses.monthly_hoa, minimum=0.0),
        "monthly_property_management": _coerce_float(expenses.monthly_property_management, minimum=0.0),
        "monthly_maintenance_reserve": _coerce_float(expenses.monthly_maintenance_reserve, minimum=0.0),
        "monthly_owner_paid_utilities": _coerce_float(expenses.monthly_owner_paid_utilities, minimum=0.0),
        "monthly_other_expenses": _coerce_float(expenses.monthly_other_expenses, minimum=0.0),
        "rent_ready_repairs": _coerce_float(verdict_inputs.rent_ready_repairs, minimum=0.0),
    }


def _ensure_wizard_state(deal_profile) -> None:
    if "deal_wizard_step" not in st.session_state:
        st.session_state["deal_wizard_step"] = 0
    if st.session_state.get(DRAFT_DEAL_ID_KEY) != deal_profile.id:
        for field_name, value in _seed_draft_values(deal_profile).items():
            st.session_state[_draft_key(field_name)] = value
        st.session_state[DRAFT_DEAL_ID_KEY] = deal_profile.id
        st.session_state[FEEDBACK_KEY] = {}


def _sync_draft_to_profile(deal_profile) -> None:
    property_details = deal_profile.property_details
    acquisition_details = deal_profile.acquisition_details
    verdict_inputs = deal_profile.verdict_inputs
    capital_details = deal_profile.capital_markets_details
    expenses = deal_profile.expense_line_items

    property_details.address = str(st.session_state.get(_draft_key("address"), "")).strip()
    property_details.asset_type = st.session_state.get(_draft_key("asset_type"), property_details.asset_type)
    property_details.sq_ft = _coerce_int(st.session_state.get(_draft_key("sq_ft")), minimum=0)
    property_details.year_built = _coerce_int(
        st.session_state.get(_draft_key("year_built")),
        minimum=1800,
        maximum=2100,
    )
    property_details.state = st.session_state.get(_draft_key("state"), property_details.state)

    acquisition_details.purchase_price = _coerce_int(
        st.session_state.get(_draft_key("purchase_price")),
        minimum=0,
    )

    verdict_inputs.monthly_rent = _coerce_float(
        st.session_state.get(_draft_key("monthly_rent")),
        minimum=0.0,
    )
    verdict_inputs.monthly_other_income = _coerce_float(
        st.session_state.get(_draft_key("monthly_other_income")),
        minimum=0.0,
    )
    verdict_inputs.vacancy_pct = _coerce_int(
        st.session_state.get(_draft_key("vacancy_pct")),
        minimum=0,
        maximum=20,
    )
    verdict_inputs.rent_ready_repairs = _coerce_float(
        st.session_state.get(_draft_key("rent_ready_repairs")),
        minimum=0.0,
    )

    deal_profile.other_details["wizard_financing_mode"] = st.session_state.get(
        _draft_key("wizard_financing_mode"),
        "LTV %",
    )
    capital_details.loan_type = st.session_state.get(_draft_key("loan_type"), capital_details.loan_type)
    capital_details.ltv_pct = _coerce_int(
        st.session_state.get(_draft_key("ltv_pct")),
        minimum=50,
        maximum=97,
    )
    capital_details.down_payment = _coerce_float(
        st.session_state.get(_draft_key("down_payment")),
        minimum=0.0,
    )
    capital_details.interest_rate_pct = _coerce_float(
        st.session_state.get(_draft_key("interest_rate_pct")),
        minimum=0.0,
        maximum=20.0,
    )
    capital_details.term_years = _coerce_int(
        st.session_state.get(_draft_key("term_years")),
        minimum=15,
        maximum=30,
    )
    capital_details.closing_costs_pct = _coerce_int(
        st.session_state.get(_draft_key("closing_costs_pct")),
        minimum=0,
        maximum=7,
    )

    expenses.annual_property_taxes = _coerce_float(
        st.session_state.get(_draft_key("annual_property_taxes")),
        minimum=0.0,
    )
    expenses.annual_insurance = _coerce_float(
        st.session_state.get(_draft_key("annual_insurance")),
        minimum=0.0,
    )
    expenses.monthly_hoa = _coerce_float(
        st.session_state.get(_draft_key("monthly_hoa")),
        minimum=0.0,
    )
    expenses.monthly_property_management = _coerce_float(
        st.session_state.get(_draft_key("monthly_property_management")),
        minimum=0.0,
    )
    expenses.monthly_maintenance_reserve = _coerce_float(
        st.session_state.get(_draft_key("monthly_maintenance_reserve")),
        minimum=0.0,
    )
    expenses.monthly_owner_paid_utilities = _coerce_float(
        st.session_state.get(_draft_key("monthly_owner_paid_utilities")),
        minimum=0.0,
    )
    expenses.monthly_other_expenses = _coerce_float(
        st.session_state.get(_draft_key("monthly_other_expenses")),
        minimum=0.0,
    )


def _refresh_wizard_profile(deal_profile) -> None:
    _sync_draft_to_profile(deal_profile)
    refresh_deal_calculations(deal_profile)


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
    # Per the state refresh plan, navigation actions should only handle validation
    # and step changes. Data persistence and recalculation are handled automatically
    # on each rerun by `_refresh_wizard_profile` at the top of the component.
    if not _validate_current_step(step_key, deal_profile):
        return False
    if go_next:
        _go_to_next_step()
    return True


def _draft_select(label: str, field_name: str, options, *, help_text: Optional[str] = None) -> None:
    current_value = st.session_state.get(_draft_key(field_name), options[0] if options else "")
    st.selectbox(
        label,
        options=options,
        index=get_safe_index(options, current_value),
        key=_draft_key(field_name),
        help=help_text,
    )


def _draft_text(label: str, field_name: str) -> None:
    draft_key = _draft_key(field_name)
    st.text_input(
        label,
        value=st.session_state.get(draft_key, ""),
        key=draft_key
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
    draft_key = _draft_key(field_name)
    
    kwargs = {
        "label": label,
        "min_value": minimum,
        "value": st.session_state.get(draft_key, minimum),
        "step": step,
        "key": draft_key,
        "help": help_text,
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
    draft_key = _draft_key(field_name)
    
    st.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        value=st.session_state.get(draft_key, minimum),
        step=step,
        key=draft_key,
        help=help_text,
    )


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
        "Other Monthly Income",
        "monthly_other_income",
        minimum=0.0,
        step=25.0,
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
    if _coerce_int(st.session_state.get(_draft_key("purchase_price")), minimum=0) <= 0:
        st.warning("Set the asking price first in Step 1.")
        return

    capital_details = deal_profile.capital_markets_details
    _draft_select("Loan Type", "loan_type", LOAN_TYPE_OPTIONS)
    _draft_select("Financing Input Mode", "wizard_financing_mode", FINANCING_MODE_OPTIONS)

    financing_mode = st.session_state.get(_draft_key("wizard_financing_mode"), "LTV %")
    purchase_price = float(_coerce_int(st.session_state.get(_draft_key("purchase_price")), minimum=0))

    col1, col2, col3 = st.columns(3)
    with col1:
        if financing_mode == "LTV %":
            _draft_slider("Loan-to-Value (LTV) %", "ltv_pct", minimum=50, maximum=97, step=1)
        else:
            _draft_number_input(
                "Down Payment ($)",
                "down_payment",
                minimum=0.0,
                maximum=float(purchase_price),
                step=5000.0,
            )

        _draft_number_input(
            "Interest Rate (%)",
            "interest_rate_pct",
            minimum=0.0,
            maximum=20.0,
            step=0.125,
        )
    with col2:
        _draft_select("Loan Term (Years)", "term_years", [30, 25, 20, 15])
        _draft_slider("Closing Costs (%)", "closing_costs_pct", minimum=0, maximum=7, step=1)
    with col3:
        st.metric("Loan Amount", f"${capital_details.loan_amount:,.0f}")
        st.metric("Down Payment", f"${capital_details.down_payment:,.0f}")
        st.metric("Implied LTV", f"{capital_details.ltv_pct}%")

    st.info(
        f"Estimated monthly principal and interest: ${capital_details.monthly_payment:,.0f}. "
        f"Estimated cash to close before rent-ready repairs: "
        f"${capital_details.down_payment + capital_details.closing_costs:,.0f}."
    )

    action = _show_step_actions("Back to Rent", "Continue to Expenses")
    if action == "previous":
        _go_to_previous_step()
        st.rerun()
    if action == "next" and _save_step("financing", deal_profile, go_next=True):
        st.rerun()


def _render_expenses_step(deal_profile) -> None:
    asset_type = st.session_state.get(_draft_key("asset_type"), "")

    st.markdown(
        "Enter the recurring and one-time costs that affect profitability, cash flow, and the final verdict."
    )
    if asset_type in HOA_REQUIRED_ASSET_TYPES:
        st.info(f"{asset_type} deals require an HOA amount because it affects profitability directly.")

    col1, col2 = st.columns(2)
    with col1:
        _draft_number_input("Annual Property Taxes", "annual_property_taxes", minimum=0.0, step=250.0)
        _draft_number_input("Annual Insurance", "annual_insurance", minimum=0.0, step=100.0)
        _draft_number_input("Monthly HOA", "monthly_hoa", minimum=0.0, step=25.0)
        _draft_number_input(
            "Monthly Property Management",
            "monthly_property_management",
            minimum=0.0,
            step=25.0,
        )
    with col2:
        _draft_number_input(
            "Monthly Maintenance / Reserve",
            "monthly_maintenance_reserve",
            minimum=0.0,
            step=25.0,
        )
        _draft_number_input(
            "Monthly Owner-Paid Utilities",
            "monthly_owner_paid_utilities",
            minimum=0.0,
            step=25.0,
        )
        _draft_number_input(
            "Other Monthly Expenses",
            "monthly_other_expenses",
            minimum=0.0,
            step=25.0,
        )
        _draft_number_input(
            "One-Time Rent-Ready Repairs",
            "rent_ready_repairs",
            minimum=0.0,
            step=500.0,
            help_text="Use this for small make-ready work. Heavy rehab is out of scope for this workflow.",
        )

    action = _show_step_actions("Back to Financing", "Continue to Verdict")
    if action == "previous":
        _go_to_previous_step()
        st.rerun()
    if action == "next" and _save_step("expenses", deal_profile, go_next=True):
        st.rerun()


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
            st.session_state["deal_profile"] = type(deal_profile)()
            st.session_state["deal_wizard_step"] = 0
            st.session_state.pop(DRAFT_DEAL_ID_KEY, None)
            st.session_state.pop(FEEDBACK_KEY, None)
            for field_name in FIELD_LABELS:
                st.session_state.pop(_draft_key(field_name), None)
            st.rerun()


def show_deal_verdict_wizard() -> None:
    """Displays the primary guided workflow for single-deal passive rental analysis."""
    deal_profile = st.session_state["deal_profile"]
    _ensure_wizard_state(deal_profile)
    _refresh_wizard_profile(deal_profile)

    step_index = st.session_state["deal_wizard_step"]
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
    _run_step(step_key, lambda: renderers[step_key](deal_profile))
    if step_key != "verdict":
        _render_live_verdict_preview(deal_profile)
    _show_feedback(step_key)
