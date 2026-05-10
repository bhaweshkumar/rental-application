from pathlib import Path


SRC_DIR = Path(__file__).resolve().parents[1]


def test_verdict_related_pages_no_longer_use_form_gated_inputs():
    page_paths = [
        SRC_DIR / "market_regulatory_intake.py",
        SRC_DIR / "acquisition_rehab_modeler.py",
        SRC_DIR / "capital_markets_simulator.py",
        SRC_DIR / "underwriting_engine.py",
    ]

    for page_path in page_paths:
        source = page_path.read_text()
        assert "with st.form(" not in source, page_path.name
        assert "st.form_submit_button" not in source, page_path.name
