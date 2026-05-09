import subprocess
import sys
import textwrap
from pathlib import Path


def test_app_imports_from_src_directory():
    """The Streamlit entrypoint must import successfully when launched from src/."""
    src_dir = Path(__file__).resolve().parents[1]
    script = textwrap.dedent(
        """
        import sys
        import types

        sys.modules['streamlit'] = types.ModuleType('streamlit')
        sys.modules['pandas'] = types.ModuleType('pandas')

        import app

        print(app.__name__)
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=src_dir,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
