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


# ── session persistence tests (cross-step data survival) ─────────────────

def test_sync_draft_skips_absent_keys_and_preserves_profile():
    """
    _sync_draft_to_profile must NOT zero-out profile fields whose draft keys have
    been removed from session_state (Streamlit 1.34+ widget-state cleanup).

    Scenario: user filled Step 1 (purchase_price=350 000, state='Texas'); the wizard
    advanced to Step 2 and Streamlit cleaned up Step 1 widget keys.  Only the
    monthly_rent key (current step) is present.  The profile must keep its Step 1
    values intact and only update monthly_rent from the surviving draft key.
    """
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()

    deal = DealProfile()
    deal.acquisition_details.purchase_price = 350_000
    deal.property_details.state = "Texas"
    deal.property_details.sq_ft = 1_800

    # Only the Rent step key is present; all Step 1 keys were cleaned up by Streamlit.
    wizard.st.session_state[draft_key("monthly_rent")] = 3_200.0

    wizard._sync_draft_to_profile(deal)

    # Present key must update the profile.
    assert deal.verdict_inputs.monthly_rent == 3_200.0
    # Absent keys must leave the profile untouched — not zeroed out.
    assert deal.acquisition_details.purchase_price == 350_000
    assert deal.property_details.state == "Texas"
    assert deal.property_details.sq_ft == 1_800


def test_restore_missing_draft_keys_fills_gaps_without_overwriting_present_keys():
    """
    _restore_missing_draft_keys must write profile values into session_state only
    for keys that are absent; keys that are already present (the user's in-progress
    edits on the current step) must be left untouched.
    """
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()

    deal = DealProfile()
    deal.acquisition_details.purchase_price = 400_000
    deal.verdict_inputs.monthly_rent = 2_500.0
    deal.property_details.state = "Florida"

    # monthly_rent is in session_state with the user's in-progress edit (different
    # from the profile value); purchase_price is absent (cleaned up by Streamlit).
    wizard.st.session_state[draft_key("monthly_rent")] = 2_900.0

    wizard._restore_missing_draft_keys(deal)

    # Absent key must be restored from the profile.
    assert wizard.st.session_state.get(draft_key("purchase_price")) == 400_000
    assert wizard.st.session_state.get(draft_key("state")) == "Florida"
    # Present key must NOT be overwritten with the profile value.
    assert wizard.st.session_state.get(draft_key("monthly_rent")) == 2_900.0


def test_refresh_wizard_profile_preserves_all_step_data_across_navigation():
    """
    Full lifecycle test: data entered on Step 1 must survive navigation to Step 2
    even when Streamlit removes Step 1 widget keys from session_state.

    Sequence simulated:
      1. User fills Step 1 → profile is synced → all draft keys populated.
      2. User navigates to Step 2; Streamlit removes Step 1 widget keys.
      3. _refresh_wizard_profile runs for Step 2.

    Expected outcome:
      - Profile retains Step 1 values (purchase_price, state, sq_ft).
      - Profile reflects Step 2 user input (monthly_rent).
      - Step 1 draft keys are restored in session_state for when the user navigates back.
    """
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()

    deal = DealProfile()
    # Simulate the profile as it would be after a successful Step 1 sync.
    deal.acquisition_details.purchase_price = 275_000
    deal.property_details.address = "42 Elm St"
    deal.property_details.state = "Texas"
    deal.property_details.sq_ft = 1_400
    deal.property_details.year_built = 2005
    deal.capital_markets_details.ltv_pct = 75
    deal.capital_markets_details.interest_rate_pct = 7.5
    deal.capital_markets_details.term_years = 30
    deal.capital_markets_details.closing_costs_pct = 3
    deal.other_details["wizard_financing_mode"] = "LTV %"

    # Step 2 is now active; only Rent step keys are present in session_state.
    # Step 1 keys have been removed by Streamlit's widget-state cleanup.
    wizard.st.session_state[draft_key("monthly_rent")] = 2_200.0
    wizard.st.session_state[draft_key("monthly_other_income")] = 0.0
    wizard.st.session_state[draft_key("vacancy_pct")] = 5

    wizard._refresh_wizard_profile(deal)

    # Profile must retain all Step 1 data.
    assert deal.acquisition_details.purchase_price == 275_000, \
        "purchase_price was corrupted to zero — absent draft key was not skipped"
    assert deal.property_details.state == "Texas"
    assert deal.property_details.sq_ft == 1_400
    assert deal.property_details.year_built == 2005

    # Profile must reflect the Step 2 user input.
    assert deal.verdict_inputs.monthly_rent == 2_200.0

    # Step 1 draft keys must be restored so the user sees correct values on back-navigation.
    assert wizard.st.session_state.get(draft_key("purchase_price")) == 275_000, \
        "purchase_price draft key was not restored from profile after step navigation"
    assert wizard.st.session_state.get(draft_key("state")) == "Texas"
    assert wizard.st.session_state.get(draft_key("address")) == "42 Elm St"

    # Step 2 draft keys must not have been overwritten with profile defaults.
    assert wizard.st.session_state.get(draft_key("monthly_rent")) == 2_200.0
