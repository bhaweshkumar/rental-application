import importlib
import sys
import types
from pathlib import Path

from src.logic.models import DealProfile


SRC_DIR = Path(__file__).resolve().parents[1]


def _load_wizard_module():
    streamlit_stub = types.ModuleType("streamlit")
    streamlit_stub.session_state = {}
    sys.modules["streamlit"] = streamlit_stub
    sys.modules.setdefault("pandas", types.ModuleType("pandas"))
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    for module_name in [
        "shared.constants",
        "shared.utils",
        "verdict_summary",
        "logic.financing",
        "logic.verdict",
        "deal_verdict_wizard",
    ]:
        sys.modules.pop(module_name, None)

    return importlib.import_module("deal_verdict_wizard")


def test_initialize_wizard_draft_state_uses_typed_profile_values():
    wizard = _load_wizard_module()
    deal = DealProfile()
    deal.property_details.sq_ft = 1234.9
    deal.property_details.year_built = 1999.4
    deal.acquisition_details.purchase_price = 250000.8
    deal.capital_markets_details.interest_rate_pct = 7
    deal.expense_line_items.monthly_hoa = 275
    wizard.st.session_state.clear()

    wizard._ensure_wizard_state(deal)

    assert wizard.st.session_state[wizard._draft_key("sq_ft")] == 1234
    assert wizard.st.session_state[wizard._draft_key("year_built")] == 1999
    assert wizard.st.session_state[wizard._draft_key("purchase_price")] == 250000
    assert wizard.st.session_state[wizard._draft_key("interest_rate_pct")] == 7.0
    assert wizard.st.session_state[wizard._draft_key("monthly_hoa")] == 275.0


def test_step_status_summary_uses_friendly_labels_for_missing_fields():
    wizard = _load_wizard_module()
    deal = DealProfile()
    deal.property_details.asset_type = "Condo"
    wizard._sync_draft_to_profile(deal)

    summary = wizard._get_step_status_summary(deal)

    assert "Property" in summary
    assert "Expenses" in summary
    assert "Property Address" in summary["Property"]
    assert "Monthly HOA" in summary["Expenses"]


def test_go_to_step_clamps_navigation_range():
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()
    wizard.st.session_state["deal_wizard_step"] = 0

    wizard._go_to_step(99)
    assert wizard.st.session_state["deal_wizard_step"] == len(wizard.WIZARD_STEPS) - 1

    wizard._go_to_step(-5)
    assert wizard.st.session_state["deal_wizard_step"] == 0


def test_run_step_returns_friendly_error_state():
    wizard = _load_wizard_module()
    wizard.st.session_state.clear()
    wizard._set_step_error("rent", "")

    def broken():
        raise ValueError("bad widget state")

    ok = wizard._run_step("rent", broken)

    assert ok is False
    assert "We hit an unexpected error" in wizard._get_step_error("rent")
    assert "bad widget state" in wizard._get_step_error("rent")
