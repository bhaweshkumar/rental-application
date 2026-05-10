"""Tests that pages use live-update rather than form-gated inputs."""
from pathlib import Path

PAGES_DIR = Path(__file__).resolve().parents[1] / "rental_platform" / "pages"


def test_verdict_related_pages_no_longer_use_form_gated_inputs():
    """All deal-analysis pages must update the shared profile immediately, not via st.form."""
    page_names = [
        "market_regulatory_intake.py",
        "acquisition_rehab_modeler.py",
        "capital_markets_simulator.py",
        "underwriting_engine.py",
    ]
    for page_name in page_names:
        page_path = PAGES_DIR / page_name
        source = page_path.read_text()
        assert "with st.form(" not in source, f"{page_name} uses st.form"
        assert "st.form_submit_button" not in source, f"{page_name} uses form_submit_button"
