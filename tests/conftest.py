"""Shared test fixtures."""
import sys
import pytest
from rental_platform.models import DealProfile


@pytest.fixture
def default_profile() -> DealProfile:
    return DealProfile()


@pytest.fixture(autouse=True)
def _restore_streamlit_after_stub_tests():
    """Restore the real streamlit module after any test that replaces it with a stub.

    Several wizard tests use a minimal Streamlit stub via sys.modules['streamlit']
    for fast, isolated testing. Without cleanup two things go wrong for AppTest tests
    that follow:

    1. The stub is returned by `import streamlit` (AttributeError on st.secrets).
    2. rental_platform.pages.* and rental_platform.session.* modules that were already
       imported against the stub remain cached in sys.modules, so AppTest picks them up
       with the stub's st (AttributeError on st.header, etc.).

    Both are fixed here: restore the real streamlit and evict any stub-tainted
    rental_platform page/session modules so they are reimported fresh next run.
    """
    original = sys.modules.get("streamlit")
    yield
    current = sys.modules.get("streamlit")
    if original is not None:
        sys.modules["streamlit"] = original
    elif "streamlit" in sys.modules:
        del sys.modules["streamlit"]
    # If the stub replaced streamlit, purge rental_platform modules that were
    # imported against it so they reload with the real streamlit next time.
    if current is not original:
        for mod in list(sys.modules.keys()):
            if mod.startswith("rental_platform.pages") or mod.startswith("rental_platform.session"):
                sys.modules.pop(mod, None)
