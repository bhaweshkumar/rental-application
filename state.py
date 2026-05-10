import streamlit as st
from typing import Any

from src.models import DealProfile

# This mapping defines the relationship between session_state draft keys
# and the attributes of the DealProfile object.
# The key is the draft key in st.session_state.
# The value is the dot-separated path to the attribute in the DealProfile object.
DRAFT_TO_PROFILE_MAPPING = {
    # Acquisition
    "draft_purchase_price": "acquisition.purchase_price",

    # Rent
    "draft_projected_monthly_rent": "underwriting.projected_monthly_gross_rent",

    # Financing
    "draft_down_payment_percent": "financing.down_payment_percent",
    "draft_interest_rate": "financing.interest_rate",
    "draft_loan_term_years": "financing.loan_term_years",

    # Expenses
    "draft_total_monthly_expenses": "underwriting.total_monthly_expenses",
}


def _set_nested_attr(obj: Any, path: str, value: Any):
    """Helper to set a nested attribute on an object using a dot-separated path."""
    keys = path.split('.')
    for key in keys[:-1]:
        obj = getattr(obj, key)
    setattr(obj, keys[-1], value)


def _get_nested_attr(obj: Any, path: str, default: Any = None) -> Any:
    """Helper to get a nested attribute from an object using a dot-separated path."""
    keys = path.split('.')
    for key in keys:
        try:
            obj = getattr(obj, key)
        except AttributeError:
            return default
    return obj


def initialize_session_state():
    """
    Initializes session state with a default DealProfile and draft keys
    if they don't already exist. This function is idempotent and safe to
    call on every page rerun.
    """
    if "deal_profile" not in st.session_state:
        st.session_state.deal_profile = DealProfile()

    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 0

    # Initialize draft keys from the profile only if they haven't been set up yet.
    # This prevents overwriting user input on subsequent reruns.
    if "draft_keys_initialized" not in st.session_state:
        for draft_key, profile_path in DRAFT_TO_PROFILE_MAPPING.items():
            value = _get_nested_attr(st.session_state.deal_profile, profile_path)
            if value is not None:
                st.session_state[draft_key] = value
        st.session_state.draft_keys_initialized = True


def _sync_draft_to_profile(deal_profile: DealProfile):
    """
    Syncs values from 'draft_' keys in session_state to the deal_profile object.
    This is the one-way flow from UI draft state to the canonical deal profile.
    """
    for draft_key, profile_path in DRAFT_TO_PROFILE_MAPPING.items():
        if draft_key in st.session_state:
            _set_nested_attr(deal_profile, profile_path, st.session_state[draft_key])