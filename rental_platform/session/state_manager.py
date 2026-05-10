"""
Centralised Streamlit session state management.

Session state keys (canonical):
  deal_profile                     — canonical DealProfile dataclass
  profile_version                  — int, incremented on every external mutation
  deal_wizard_step                 — int, current wizard step index (0-based)
  deal_wizard_draft_{field}        — per-field wizard editing buffers
  deal_wizard_last_seen_version    — profile_version at last wizard draft seed
  deal_wizard_draft_deal_id        — deal id active when drafts were last seeded
  deal_wizard_feedback             — dict of per-step validation messages
"""
import streamlit as st

from rental_platform.models import DealProfile

# ── key constants ─────────────────────────────────────────────────────────
DRAFT_PREFIX = "deal_wizard_draft"
WIZARD_STEP_KEY = "deal_wizard_step"
PROFILE_VERSION_KEY = "profile_version"
WIZARD_LAST_SEEN_VERSION_KEY = "deal_wizard_last_seen_version"
WIZARD_DRAFT_DEAL_ID_KEY = "deal_wizard_draft_deal_id"
WIZARD_FEEDBACK_KEY = "deal_wizard_feedback"


def draft_key(field_name: str) -> str:
    """Returns the session-state key used for a wizard draft field."""
    return f"{DRAFT_PREFIX}_{field_name}"


# ── app-level initialisation ─────────────────────────────────────────────
def initialize_session_state() -> None:
    """Idempotent. Call once at application entry (app.py)."""
    if "deal_profile" not in st.session_state:
        st.session_state["deal_profile"] = DealProfile()
    if PROFILE_VERSION_KEY not in st.session_state:
        st.session_state[PROFILE_VERSION_KEY] = 0
    if WIZARD_STEP_KEY not in st.session_state:
        st.session_state[WIZARD_STEP_KEY] = 0
    if WIZARD_LAST_SEEN_VERSION_KEY not in st.session_state:
        st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = -1


# ── profile mutation signalling ──────────────────────────────────────────
def mark_profile_mutated() -> None:
    """
    Call after any non-wizard page writes to the canonical deal_profile.
    This causes the wizard to reseed its draft values on next render,
    preventing stale wizard inputs from overwriting the new data.
    """
    st.session_state[PROFILE_VERSION_KEY] = (
        st.session_state.get(PROFILE_VERSION_KEY, 0) + 1
    )


def get_deal_profile() -> DealProfile:
    """Returns the canonical deal profile from session state."""
    return st.session_state["deal_profile"]


# ── deal reset ───────────────────────────────────────────────────────────
def reset_deal() -> None:
    """Clears the canonical profile and all wizard draft state for a fresh start."""
    profile_type = type(st.session_state.get("deal_profile", DealProfile()))
    st.session_state["deal_profile"] = profile_type()
    st.session_state[PROFILE_VERSION_KEY] = 0
    st.session_state[WIZARD_STEP_KEY] = 0
    st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = -1
    st.session_state.pop(WIZARD_DRAFT_DEAL_ID_KEY, None)
    st.session_state.pop(WIZARD_FEEDBACK_KEY, None)
    for k in [key for key in st.session_state if key.startswith(DRAFT_PREFIX + "_")]:
        del st.session_state[k]


# ── wizard draft synchronisation ─────────────────────────────────────────
def should_reseed_wizard_drafts() -> bool:
    """
    Returns True when the wizard must reseed its draft buffers from the
    canonical profile. This happens when:
      - An external page has mutated the profile since the wizard last ran, OR
      - The deal id has changed (new deal or reset).
    """
    current_version = st.session_state.get(PROFILE_VERSION_KEY, 0)
    last_seen = st.session_state.get(WIZARD_LAST_SEEN_VERSION_KEY, -1)
    current_deal_id = getattr(st.session_state.get("deal_profile"), "id", None)
    seeded_deal_id = st.session_state.get(WIZARD_DRAFT_DEAL_ID_KEY)
    return (current_version != last_seen) or (current_deal_id != seeded_deal_id)


def mark_wizard_synced() -> None:
    """Record that the wizard has seeded its drafts from the current profile version."""
    st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = st.session_state.get(PROFILE_VERSION_KEY, 0)
    st.session_state[WIZARD_DRAFT_DEAL_ID_KEY] = getattr(
        st.session_state.get("deal_profile"), "id", None
    )


def go_to_wizard_step(step_index: int, total_steps: int) -> None:
    """Navigate the wizard to a specific step, clamped to valid range."""
    st.session_state[WIZARD_STEP_KEY] = max(0, min(step_index, total_steps - 1))
