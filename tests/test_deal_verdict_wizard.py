"""Tests for the Deal Verdict Wizard session management and step logic."""
import importlib
import sys
import types
from pathlib import Path

from rental_platform.models import DealProfile
from rental_platform.session.state_manager import (
    WIZARD_STEP_KEY,
    WIZARD_FEEDBACK_KEY,
    DRAFT_PREFIX,
    draft_key,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_wizard_module():
    """Load the wizard page module with a minimal Streamlit stub."""
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.session_state = {}
    sys.modules["streamlit"] = streamlit_stub
    sys.modules.setdefault("pandas", types.ModuleType("pandas"))

    # Reload to pick up stub
    for mod in list(sys.modules.keys()):
        if mod.startswith("rental_platform.pages") or mod.startswith("rental_platform.session"):
            sys.modules.pop(mod, None)

    return importlib.import_module("rental_platform.pages.deal_verdict_wizard")


def test_seed_draft_values_coerces_floats_to_correct_types():
    """_seed_draft_values must return typed (int/float) values for all numeric fields."""
    wizard = _load_wizard_module()
    deal = DealProfile()
    deal.property_details.sq_ft = 1234.9
    deal.property_details.year_built = 1999.4
    deal.acquisition_details.purchase_price = 250000.8
    deal.capital_markets_details.interest_rate_pct = 7
    deal.expense_line_items.monthly_hoa = 275

    values = wizard._seed_draft_values(deal)

    assert values["sq_ft"] == 1234
    assert values["year_built"] == 1999
    assert values["purchase_price"] == 250000
    assert values["interest_rate_pct"] == 7.0
    assert values["monthly_hoa"] == 275.0


def test_ensure_wizard_drafts_seeds_state_on_first_render():
    """_ensure_wizard_drafts must populate all draft keys when called fresh."""
    wizard = _load_wizard_module()
    # Patch session state and state manager functions
    wizard.st.session_state.clear()
    wizard.st.session_state["profile_version"] = 0
    wizard.st.session_state["deal_wizard_last_seen_version"] = -1  # triggers reseed

    deal = DealProfile()
    deal.property_details.address = "123 Test St"
    deal.acquisition_details.purchase_price = 300000

    wizard._ensure_wizard_drafts(deal)

    assert wizard.st.session_state.get(draft_key("address")) == "123 Test St"
    assert wizard.st.session_state.get(draft_key("purchase_price")) == 300000


def test_go_to_step_clamps_navigation_range():
    """_go_to_step must clamp the step index to valid bounds."""
    wizard = _load_wizard_module()
    wizard.st.session_state[WIZARD_STEP_KEY] = 2

    wizard._go_to_step(-5)
    assert wizard.st.session_state[WIZARD_STEP_KEY] == 0

    wizard._go_to_step(999)
    assert wizard.st.session_state[WIZARD_STEP_KEY] == len(wizard.WIZARD_STEPS) - 1


def test_format_missing_fields_uses_friendly_labels():
    """_format_missing_fields should return human-readable labels."""
    wizard = _load_wizard_module()
    result = wizard._format_missing_fields(["address", "purchase_price", "monthly_rent"])
    assert "Property Address" in result
    assert "Asking Price" in result
    assert "Expected Monthly Rent" in result


def test_validate_current_step_sets_warning_on_missing_fields():
    """_validate_current_step should set feedback when required fields are empty."""
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()
    deal = DealProfile()  # all defaults — property step will have missing fields

    result = wizard._validate_current_step("property", deal)

    assert result is False
    feedback = wizard.st.session_state.get(WIZARD_FEEDBACK_KEY, {})
    assert "property" in feedback
    assert feedback["property"]["level"] == "warning"


def test_wizard_pages_do_not_use_streamlit_forms():
    """The wizard source must not gate inputs behind st.form (live-update pattern)."""
    import inspect
    wizard = _load_wizard_module()
    source = inspect.getsource(wizard)
    assert "with st.form(" not in source
    assert "st.form_submit_button" not in source
