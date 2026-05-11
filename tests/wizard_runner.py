"""
Minimal Streamlit script used as the AppTest entry point for wizard integration tests.

Runs only the Deal Verdict Wizard page so tests do not depend on the full
multi-page app.py navigation tree.
"""
import streamlit as st  # noqa: F401 — imported so AppTest can patch it

from rental_platform.session import initialize_session_state
from rental_platform.pages.deal_verdict_wizard import show_deal_verdict_wizard

initialize_session_state()
show_deal_verdict_wizard()
