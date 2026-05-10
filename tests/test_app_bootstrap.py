import subprocess
import sys
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_app_imports_cleanly():
    """Root app.py must import successfully from the repo root."""
    script = textwrap.dedent("""
        import sys, types
        sys.modules["streamlit"] = types.ModuleType("streamlit")
        sys.modules["pandas"] = types.ModuleType("pandas")
        import app
        print(app.__name__)
    """)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_deal_verdict_wizard_imports_from_new_package():
    """The new wizard page must import successfully from the repo root."""
    script = textwrap.dedent("""
        import sys, types
        sys.modules["streamlit"] = types.ModuleType("streamlit")
        sys.modules["pandas"] = types.ModuleType("pandas")
        from rental_platform.pages.deal_verdict_wizard import show_deal_verdict_wizard
        print(show_deal_verdict_wizard.__name__)
    """)
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
