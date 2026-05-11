"""
Integration tests for the Deal Verdict Wizard.

Two testing layers:

AppTest layer — verifies on_change callbacks fire immediately (committing data
to deal_profile) and that data survives one-step forward navigation. Uses
streamlit.testing.v1.AppTest for real widget lifecycle simulation.

Stub-based simulation layer — tests multi-step forward+backward navigation and
stress round-trips. Directly simulates Streamlit's widget-state cleanup (removing
draft keys for non-rendered steps) and exercises _refresh_wizard_profile across
step transitions without AppTest's between-run session-state handling quirks.
"""
import importlib
import sys
import types
import pytest
from pathlib import Path

from rental_platform.models import DealProfile
from rental_platform.session.state_manager import (
    WIZARD_STEP_KEY,
    WIZARD_LAST_SEEN_VERSION_KEY,
    draft_key,
)
from streamlit.testing.v1 import AppTest

RUNNER = str(Path(__file__).parent / "wizard_runner.py")
TIMEOUT = 30
_STEP_INDEX = {"property": 0, "rent": 1, "financing": 2, "expenses": 3, "verdict": 4}



def _setup() -> AppTest:
    at = AppTest.from_file(RUNNER, default_timeout=TIMEOUT)
    at.run()
    return at


def _nav(at: AppTest, step_key: str) -> AppTest:
    at.session_state[WIZARD_STEP_KEY] = _STEP_INDEX[step_key]
    at.run()
    return at


def _profile(at: AppTest):
    return at.session_state["deal_profile"]


# ── stub helpers ──────────────────────────────────────────────────────────

def _load_wizard():
    stub = types.ModuleType("streamlit")
    stub.session_state = {}
    sys.modules["streamlit"] = stub
    sys.modules.setdefault("pandas", types.ModuleType("pandas"))
    for mod in list(sys.modules.keys()):
        if mod.startswith("rental_platform.pages") or mod.startswith("rental_platform.session"):
            sys.modules.pop(mod, None)
    return importlib.import_module("rental_platform.pages.deal_verdict_wizard")


def _stub_setup(wiz):
    ss = wiz.st.session_state
    deal = DealProfile()
    ss["deal_profile"] = deal
    ss["profile_version"] = 0
    ss[WIZARD_STEP_KEY] = 0
    ss[WIZARD_LAST_SEEN_VERSION_KEY] = -1
    wiz._ensure_wizard_drafts(deal)
    wiz._refresh_wizard_profile(deal)
    return deal


def _simulate_cleanup(wiz, active_step: str):
    """Remove draft keys for all steps except active_step (Streamlit widget cleanup)."""
    from rental_platform.pages.deal_verdict_wizard import STEP_FIELDS
    ss = wiz.st.session_state
    for step_key, fields in STEP_FIELDS.items():
        if step_key != active_step:
            for field in fields:
                ss.pop(draft_key(field), None)


def _commit(wiz, field_name: str, value):
    """Simulate a user widget interaction: set draft key then fire on_change."""
    wiz.st.session_state[draft_key(field_name)] = value
    wiz._on_field_change(field_name)


def _go_to(wiz, deal, step: str):
    """Simulate step transition: cleanup non-active widget keys, refresh profile."""
    _simulate_cleanup(wiz, step)
    wiz._refresh_wizard_profile(deal)


# ── AppTest: on_change fires immediately ──────────────────────────────────

def test_rent_on_change_commits_to_profile_immediately():
    at = _setup()
    _nav(at, "rent")
    at.number_input(key=draft_key("monthly_rent")).set_value(2_800.0).run()
    assert _profile(at).verdict_inputs.monthly_rent == pytest.approx(2_800.0), (
        "monthly_rent not committed to profile by on_change"
    )


def test_financing_on_change_commits_to_profile_immediately():
    at = _setup()
    _nav(at, "financing")
    at.number_input(key=draft_key("interest_rate_pct")).set_value(8.75).run()
    assert _profile(at).capital_markets_details.interest_rate_pct == pytest.approx(8.75), (
        "interest_rate_pct not committed to profile by on_change"
    )


def test_expenses_on_change_commits_to_profile_immediately():
    at = _setup()
    _nav(at, "expenses")
    at.number_input(key=draft_key("annual_property_taxes")).set_value(4_800.0).run()
    assert _profile(at).expense_line_items.annual_property_taxes == pytest.approx(4_800.0), (
        "annual_property_taxes not committed to profile by on_change"
    )


def test_financing_warning_when_purchase_price_is_zero():
    at = _setup()
    at.number_input(key=draft_key("purchase_price")).set_value(0).run()
    assert _profile(at).acquisition_details.purchase_price == 0
    _nav(at, "financing")
    warning_texts = [w.value for w in at.warning]
    assert any("asking price" in t.lower() for t in warning_texts), (
        f"Expected warning not found. Rendered: {warning_texts}"
    )
    assert not at.exception


# ── AppTest: one-step forward navigation ──────────────────────────────────

def test_rent_data_survives_one_step_forward_navigation():
    at = _setup()
    _nav(at, "rent")
    at.number_input(key=draft_key("monthly_rent")).set_value(2_200.0).run()
    _nav(at, "financing")
    assert _profile(at).verdict_inputs.monthly_rent == pytest.approx(2_200.0), (
        "monthly_rent lost after one-step forward nav to Financing"
    )


def test_financing_data_survives_one_step_forward_navigation():
    at = _setup()
    _nav(at, "financing")
    at.number_input(key=draft_key("interest_rate_pct")).set_value(9.0).run()
    _nav(at, "expenses")
    assert _profile(at).capital_markets_details.interest_rate_pct == pytest.approx(9.0), (
        "interest_rate_pct lost after one-step forward nav to Expenses"
    )


def test_expenses_data_survives_one_step_forward_navigation():
    at = _setup()
    _nav(at, "expenses")
    at.number_input(key=draft_key("annual_property_taxes")).set_value(5_000.0).run()
    _nav(at, "verdict")
    assert _profile(at).expense_line_items.annual_property_taxes == pytest.approx(5_000.0), (
        "annual_property_taxes lost after one-step forward nav to Verdict"
    )


# ── Stub: multi-step forward + backward navigation ────────────────────────

def test_stub_rent_data_survives_forward_and_backward():
    """monthly_rent must survive Property→Rent→Financing→Rent with cleanup."""
    wiz = _load_wizard()
    deal = _stub_setup(wiz)

    _go_to(wiz, deal, "rent")
    _commit(wiz, "monthly_rent", 3_000.0)
    assert deal.verdict_inputs.monthly_rent == pytest.approx(3_000.0)

    _go_to(wiz, deal, "financing")
    assert deal.verdict_inputs.monthly_rent == pytest.approx(3_000.0), (
        "monthly_rent lost after forward nav to Financing"
    )
    assert wiz.st.session_state.get(draft_key("monthly_rent")) == pytest.approx(3_000.0), (
        "monthly_rent draft key not restored after forward nav"
    )

    _go_to(wiz, deal, "rent")
    assert deal.verdict_inputs.monthly_rent == pytest.approx(3_000.0), (
        "monthly_rent lost after backward nav to Rent"
    )
    assert wiz.st.session_state.get(draft_key("monthly_rent")) == pytest.approx(3_000.0), (
        "monthly_rent draft key not restored for widget on back-navigation"
    )


def test_stub_financing_data_survives_forward_and_backward():
    """interest_rate_pct must survive Financing→Expenses→Financing with cleanup."""
    wiz = _load_wizard()
    deal = _stub_setup(wiz)

    _go_to(wiz, deal, "financing")
    _commit(wiz, "interest_rate_pct", 8.5)
    assert deal.capital_markets_details.interest_rate_pct == pytest.approx(8.5)

    _go_to(wiz, deal, "expenses")
    assert deal.capital_markets_details.interest_rate_pct == pytest.approx(8.5), (
        "interest_rate_pct lost after forward nav to Expenses"
    )

    _go_to(wiz, deal, "financing")
    assert deal.capital_markets_details.interest_rate_pct == pytest.approx(8.5), (
        "interest_rate_pct lost after backward nav to Financing"
    )
    assert wiz.st.session_state.get(draft_key("interest_rate_pct")) == pytest.approx(8.5)


def test_stub_expenses_data_survives_forward_and_backward():
    """annual_property_taxes must survive Expenses→Verdict→Expenses with cleanup."""
    wiz = _load_wizard()
    deal = _stub_setup(wiz)

    _go_to(wiz, deal, "expenses")
    _commit(wiz, "annual_property_taxes", 5_500.0)
    assert deal.expense_line_items.annual_property_taxes == pytest.approx(5_500.0)

    _go_to(wiz, deal, "verdict")
    assert deal.expense_line_items.annual_property_taxes == pytest.approx(5_500.0), (
        "annual_property_taxes lost after forward nav to Verdict"
    )

    _go_to(wiz, deal, "expenses")
    assert deal.expense_line_items.annual_property_taxes == pytest.approx(5_500.0), (
        "annual_property_taxes lost after backward nav to Expenses"
    )
    assert wiz.st.session_state.get(draft_key("annual_property_taxes")) == pytest.approx(5_500.0)


# ── Stub: full workflow end-to-end ────────────────────────────────────────

def test_stub_full_workflow_all_steps_produces_valid_verdict():
    """
    Filling all four steps and computing Verdict must produce non-zero outputs.
    All step data must survive the forward traversal to Verdict.
    """
    wiz = _load_wizard()
    deal = _stub_setup(wiz)

    _go_to(wiz, deal, "property")
    _commit(wiz, "purchase_price", 275_000)
    _commit(wiz, "address", "42 Oak St Chicago IL 60601")
    _commit(wiz, "state", "Texas")
    _commit(wiz, "sq_ft", 1_200)
    _commit(wiz, "year_built", 2003)

    _go_to(wiz, deal, "rent")
    _commit(wiz, "monthly_rent", 2_500.0)
    _commit(wiz, "monthly_other_income", 100.0)
    _commit(wiz, "vacancy_pct", 5)

    _go_to(wiz, deal, "financing")
    _commit(wiz, "ltv_pct", 80)
    _commit(wiz, "interest_rate_pct", 8.25)
    _commit(wiz, "closing_costs_pct", 4)

    _go_to(wiz, deal, "expenses")
    _commit(wiz, "annual_property_taxes", 4_200.0)
    _commit(wiz, "annual_insurance", 1_200.0)
    _commit(wiz, "monthly_property_management", 150.0)
    _commit(wiz, "monthly_maintenance_reserve", 100.0)

    _go_to(wiz, deal, "verdict")

    outputs = deal.verdict_outputs
    assert outputs.total_cash_required > 0, "total_cash_required is zero — Property/Financing data lost"
    assert outputs.cap_rate > 0, f"cap_rate <= 0 ({outputs.cap_rate:.4f}) — Rent data lost before Verdict"
    assert outputs.dscr > 0, f"DSCR <= 0 — Financing or Rent data lost"
    assert deal.acquisition_details.purchase_price == 275_000
    assert deal.verdict_inputs.monthly_rent == pytest.approx(2_500.0)
    assert deal.capital_markets_details.interest_rate_pct == pytest.approx(8.25)
    assert deal.expense_line_items.annual_property_taxes == pytest.approx(4_200.0)


def test_stub_repeated_back_and_forth_preserves_all_data():
    """
    All step data must survive three complete round trips across the wizard,
    with full widget-state cleanup simulated on every step transition.
    """
    wiz = _load_wizard()
    deal = _stub_setup(wiz)

    _go_to(wiz, deal, "property")
    _commit(wiz, "purchase_price", 275_000)
    _commit(wiz, "state", "Texas")

    _go_to(wiz, deal, "rent")
    _commit(wiz, "monthly_rent", 2_500.0)
    _commit(wiz, "vacancy_pct", 5)

    _go_to(wiz, deal, "financing")
    _commit(wiz, "interest_rate_pct", 8.25)
    _commit(wiz, "ltv_pct", 80)

    _go_to(wiz, deal, "expenses")
    _commit(wiz, "annual_property_taxes", 4_200.0)
    _commit(wiz, "annual_insurance", 1_200.0)

    for _ in range(3):
        _go_to(wiz, deal, "verdict")
        _go_to(wiz, deal, "expenses")
        _go_to(wiz, deal, "financing")
        _go_to(wiz, deal, "rent")
        _go_to(wiz, deal, "property")
        _go_to(wiz, deal, "rent")
        _go_to(wiz, deal, "financing")
        _go_to(wiz, deal, "expenses")
        _go_to(wiz, deal, "verdict")

    assert deal.acquisition_details.purchase_price == 275_000, "purchase_price corrupted"
    assert deal.verdict_inputs.monthly_rent == pytest.approx(2_500.0), "monthly_rent corrupted"
    assert deal.capital_markets_details.interest_rate_pct == pytest.approx(8.25), "interest_rate_pct corrupted"
    assert deal.expense_line_items.annual_property_taxes == pytest.approx(4_200.0), "annual_property_taxes corrupted"

    _go_to(wiz, deal, "property")
    assert wiz.st.session_state.get(draft_key("purchase_price")) == 275_000

    _go_to(wiz, deal, "rent")
    assert wiz.st.session_state.get(draft_key("monthly_rent")) == pytest.approx(2_500.0)

    _go_to(wiz, deal, "financing")
    assert wiz.st.session_state.get(draft_key("interest_rate_pct")) == pytest.approx(8.25)

    _go_to(wiz, deal, "expenses")
    assert wiz.st.session_state.get(draft_key("annual_property_taxes")) == pytest.approx(4_200.0)

    _go_to(wiz, deal, "verdict")
    assert deal.verdict_outputs.cap_rate > 0, "cap_rate zero after round trips"
    assert deal.verdict_outputs.total_cash_required > 0, "total_cash_required zero after round trips"
