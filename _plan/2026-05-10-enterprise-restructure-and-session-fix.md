# Enterprise SaaS Restructure and Deal Wizard Session Fix

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the application into a standard enterprise-style Python package layout, establish one authoritative model layer, move domain logic into clearly named service modules, and fix the Deal Verdict Wizard so shared inputs across pages are preserved correctly in Streamlit session state.

**Architecture:** A new top-level package `rental_platform/` replaces the `src/` directory. Models live in `rental_platform/models/`, services in `rental_platform/services/`, Streamlit pages in `rental_platform/pages/`, and a new `rental_platform/session/` module owns all Streamlit state management. The deal wizard's draft–to–profile sync is guarded by a profile-version counter so external page edits always take precedence over stale wizard draft values.

**Tech Stack:** Python 3.9, Streamlit, dataclasses (no Pydantic in domain model), pytest

---

## Target Package Layout

```
rental-application/
├── app.py                          ← thin entry point (replaces src/app.py)
├── rental_platform/
│   ├── __init__.py
│   ├── constants/
│   │   ├── __init__.py
│   │   └── real_estate.py          ← US_STATES, ASSET_TYPE_OPTIONS, REHAB_COSTS_PER_SQFT, etc.
│   ├── models/
│   │   ├── __init__.py
│   │   └── domain.py               ← single authoritative dataclass module (from src/logic/models.py)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── financing_service.py    ← from src/logic/financing.py
│   │   ├── underwriting_service.py ← from src/logic/underwriting.py
│   │   ├── verdict_service.py      ← from src/logic/verdict.py
│   │   ├── proforma_service.py     ← from src/logic/proforma.py
│   │   ├── rehab_service.py        ← from src/logic/rehab.py
│   │   ├── brrrr_service.py        ← from src/logic/brrrr.py
│   │   ├── tax_service.py          ← from src/logic/tax.py
│   │   ├── profit_first_service.py ← from src/logic/profit_first.py
│   │   ├── crm_service.py          ← from src/logic/crm.py
│   │   └── settings_service.py     ← from src/logic/settings.py
│   ├── session/
│   │   ├── __init__.py
│   │   └── state_manager.py        ← NEW: all session init, versioning, and wizard sync
│   ├── utils/
│   │   ├── __init__.py
│   │   └── coercion.py             ← _coerce_int/_coerce_float/get_safe_index helpers
│   └── pages/
│       ├── __init__.py
│       ├── dashboard.py
│       ├── deal_verdict_wizard.py  ← updated wizard using new session manager
│       ├── market_regulatory_intake.py
│       ├── acquisition_rehab_modeler.py
│       ├── capital_markets_simulator.py
│       ├── underwriting_engine.py
│       ├── proforma_generator.py
│       ├── tax_optimizer.py
│       ├── profit_first_allocator.py
│       ├── crm_funnel.py
│       ├── deal_summary_report.py
│       ├── settings_page.py
│       └── components/
│           ├── __init__.py
│           └── verdict_summary.py  ← from src/verdict_summary.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── ... (migrated from src/test/)
└── _plan/, _spec/, etc.            ← unchanged
```

---

## Session Management Design

### Problem
`src/deal_verdict_wizard.py` calls `_ensure_wizard_state()` which seeds all draft keys once per deal id. It never re-seeds when another page (e.g. Market & Regulatory Intake) writes directly to `st.session_state["deal_profile"]`. When the user returns to the wizard, `_refresh_wizard_profile()` overwrites the canonical profile with stale draft values.

### Fix: Profile Version Counter
`StateManager` adds two integer keys to session state:
- `"profile_version"` – incremented by any page that mutates the canonical deal profile
- `"wizard_last_seen_profile_version"` – set by the wizard after each reseed

When the wizard renders, if `profile_version != wizard_last_seen_profile_version`, it reseeds all draft keys from the current canonical profile before rendering controls.

### Session State Key Policy
| Key | Owner | Description |
|-----|-------|-------------|
| `deal_profile` | StateManager | Canonical `DealProfile` dataclass |
| `profile_version` | StateManager | Int incremented on external profile mutations |
| `deal_wizard_step` | StateManager | Current wizard step index |
| `deal_wizard_draft_{field}` | WizardPage | Per-field draft buffers |
| `deal_wizard_last_seen_version` | WizardPage | Last profile_version the wizard processed |
| `deal_wizard_feedback` | WizardPage | Per-step validation messages |
| `deal_wizard_draft_deal_id` | WizardPage | Deal id used to seed current drafts |

The legacy `wizard_step` key (root `state.py`) is never initialized in the new code.

---

## Task 1: Create Package Skeleton

**Files:**
- Create: `rental_platform/__init__.py`
- Create: `rental_platform/constants/__init__.py`
- Create: `rental_platform/models/__init__.py`
- Create: `rental_platform/services/__init__.py`
- Create: `rental_platform/session/__init__.py`
- Create: `rental_platform/utils/__init__.py`
- Create: `rental_platform/pages/__init__.py`
- Create: `rental_platform/pages/components/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create all `__init__.py` files for new package**

```bash
mkdir -p rental_platform/{constants,models,services,session,utils,pages/components}
mkdir -p tests
touch rental_platform/__init__.py
touch rental_platform/constants/__init__.py
touch rental_platform/models/__init__.py
touch rental_platform/services/__init__.py
touch rental_platform/session/__init__.py
touch rental_platform/utils/__init__.py
touch rental_platform/pages/__init__.py
touch rental_platform/pages/components/__init__.py
touch tests/__init__.py
```

- [ ] **Step 2: Verify structure**

```bash
find rental_platform tests -name "*.py" | sort
```
Expected: all `__init__.py` files present, no content yet

- [ ] **Step 3: Commit skeleton**

```bash
git add rental_platform/ tests/
git commit -m "feat: scaffold rental_platform package structure"
```

---

## Task 2: Migrate Constants

**Files:**
- Create: `rental_platform/constants/real_estate.py`
- Source: `src/logic/constants.py`

- [ ] **Step 1: Write constants module**

```python
# rental_platform/constants/real_estate.py
US_STATES = [
    "", "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
    "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada",
    "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon",
    "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]

LANDLORD_FLEXIBILITY_RISK = {
    "Texas": "Low Risk (e.g., 21-28 days eviction)",
    "Indiana": "Low Risk",
    "Alabama": "Low Risk",
    "New Jersey": "High Risk (e.g., long uncontested eviction durations)",
    "California": "High Risk (e.g., long uncontested eviction durations)",
}

REHAB_COSTS_PER_SQFT = {
    "None": 0,
    "Light (Cosmetic/Paint)": 20,
    "Medium (Systems/Plumbing)": 37.5,
    "Heavy (Gut/Studs)": 65,
}

ASSET_TYPE_OPTIONS = [
    "Single-Family", "Condo", "Townhome", "2-Unit", "4-Unit", "Commercial Multifamily"
]
MARKET_PHASE_OPTIONS = ["Recovery", "Expansion", "Hyper-Supply", "Recession"]
```

- [ ] **Step 2: Update constants `__init__.py`**

```python
# rental_platform/constants/__init__.py
from .real_estate import (
    ASSET_TYPE_OPTIONS,
    LANDLORD_FLEXIBILITY_RISK,
    MARKET_PHASE_OPTIONS,
    REHAB_COSTS_PER_SQFT,
    US_STATES,
)

__all__ = [
    "ASSET_TYPE_OPTIONS",
    "LANDLORD_FLEXIBILITY_RISK",
    "MARKET_PHASE_OPTIONS",
    "REHAB_COSTS_PER_SQFT",
    "US_STATES",
]
```

- [ ] **Step 3: Commit**

```bash
git add rental_platform/constants/
git commit -m "feat: migrate constants to rental_platform.constants"
```

---

## Task 3: Migrate Domain Models

**Files:**
- Create: `rental_platform/models/domain.py`
- Source: `src/logic/models.py` (sole authoritative model source)

- [ ] **Step 1: Write domain.py** (copy `src/logic/models.py` verbatim, remove try/except import patterns since this is now the one source)

The file should contain: `PropertyDetails`, `AcquisitionDetails`, `BrrrrMetrics`, `CapitalMarketsDetails`, `UnderwritingInputs`, `UnderwritingOutputs`, `ExpenseLineItems`, `VerdictInputs`, `VerdictOutputs`, `ProformaAssumptions`, `ProformaYear`, `TaxOptimizationInputs`, `TaxOptimizationOutputs`, `ProfitFirstInputs`, `ProfitFirstOutputs`, `DealProfile`.

- [ ] **Step 2: Update models `__init__.py`** to re-export everything from `domain.py`

```python
from .domain import (
    AcquisitionDetails, BrrrrMetrics, CapitalMarketsDetails, DealProfile,
    ExpenseLineItems, ProfitFirstInputs, ProfitFirstOutputs, ProformaAssumptions,
    ProformaYear, PropertyDetails, TaxOptimizationInputs, TaxOptimizationOutputs,
    UnderwritingInputs, UnderwritingOutputs, VerdictInputs, VerdictOutputs,
)
__all__ = [...]
```

- [ ] **Step 3: Write a quick smoke test**

```python
# tests/test_models.py
from rental_platform.models import DealProfile, PropertyDetails

def test_deal_profile_defaults():
    profile = DealProfile()
    assert profile.property_details.asset_type == "Single-Family"
    assert profile.verdict_outputs.verdict_status == "Fail"
```

- [ ] **Step 4: Run test**

```bash
python -m pytest tests/test_models.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rental_platform/models/ tests/test_models.py
git commit -m "feat: consolidate domain models into rental_platform.models"
```

---

## Task 4: Migrate Services

**Files:**
- Create: `rental_platform/services/financing_service.py` ← `src/logic/financing.py`
- Create: `rental_platform/services/underwriting_service.py` ← `src/logic/underwriting.py`
- Create: `rental_platform/services/verdict_service.py` ← `src/logic/verdict.py`
- Create: `rental_platform/services/proforma_service.py` ← `src/logic/proforma.py`
- Create: `rental_platform/services/rehab_service.py` ← `src/logic/rehab.py`
- Create: `rental_platform/services/brrrr_service.py` ← `src/logic/brrrr.py`
- Create: `rental_platform/services/tax_service.py` ← `src/logic/tax.py`
- Create: `rental_platform/services/profit_first_service.py` ← `src/logic/profit_first.py`
- Create: `rental_platform/services/crm_service.py` ← `src/logic/crm.py`
- Create: `rental_platform/services/settings_service.py` ← `src/logic/settings.py`

Each service file replaces the try/except import pattern with a clean `from rental_platform.models import ...`. Function names do not change to preserve test compatibility.

- [ ] **Step 1: Create each service file** – copy logic verbatim, update all imports to use `from rental_platform.models import ...` and `from rental_platform.constants import ...`

- [ ] **Step 2: Update services `__init__.py`** with top-level re-exports of the most commonly called functions

- [ ] **Step 3: Migrate existing service tests from `src/test/` into `tests/`** – update import paths only, do not change test logic

- [ ] **Step 4: Run migrated service tests**

```bash
python -m pytest tests/ -v
```
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
git add rental_platform/services/ tests/
git commit -m "feat: migrate service logic into rental_platform.services"
```

---

## Task 5: Migrate Utils

**Files:**
- Create: `rental_platform/utils/coercion.py`
- Source: `_coerce_int`, `_coerce_float` from `src/deal_verdict_wizard.py`; `get_safe_index` from `src/logic/utils.py`

- [ ] **Step 1: Write coercion.py**

```python
# rental_platform/utils/coercion.py
from typing import Optional

def coerce_int(value, *, minimum: int = 0, maximum: Optional[int] = None) -> int:
    try:
        result = int(float(value))
    except (TypeError, ValueError):
        result = minimum
    result = max(result, minimum)
    if maximum is not None:
        result = min(result, maximum)
    return result

def coerce_float(value, *, minimum: float = 0.0, maximum: Optional[float] = None) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = minimum
    result = max(result, minimum)
    if maximum is not None:
        result = min(result, maximum)
    return result

def get_safe_index(options, value, default: int = 0) -> int:
    try:
        return list(options).index(value)
    except ValueError:
        return default
```

- [ ] **Step 2: Update utils `__init__.py`**

```python
from .coercion import coerce_int, coerce_float, get_safe_index
__all__ = ["coerce_int", "coerce_float", "get_safe_index"]
```

- [ ] **Step 3: Commit**

```bash
git add rental_platform/utils/
git commit -m "feat: create rental_platform.utils with coercion helpers"
```

---

## Task 6: Build Session Manager

**Files:**
- Create: `rental_platform/session/state_manager.py`

This is the core session management implementation. It replaces `src/app.py:initialize_session_state()`, `src/deal_verdict_wizard.py:_ensure_wizard_state()`, `src/deal_verdict_wizard.py:_sync_draft_to_profile()`, and the legacy `state.py`.

- [ ] **Step 1: Write state_manager.py**

```python
# rental_platform/session/state_manager.py
"""
Centralised Streamlit session state management.

Session state keys:
  deal_profile                     – canonical DealProfile
  profile_version                  – int, incremented on every external mutation
  deal_wizard_step                 – int, current wizard step index
  deal_wizard_draft_{field}        – per-field wizard editing buffers
  deal_wizard_last_seen_version    – profile_version at last wizard draft seed
  deal_wizard_draft_deal_id        – deal id used to seed current drafts
  deal_wizard_feedback             – dict of per-step validation messages
"""
import streamlit as st
from rental_platform.models import DealProfile

DRAFT_PREFIX = "deal_wizard_draft"
WIZARD_STEP_KEY = "deal_wizard_step"
PROFILE_VERSION_KEY = "profile_version"
WIZARD_LAST_SEEN_VERSION_KEY = "deal_wizard_last_seen_version"
WIZARD_DRAFT_DEAL_ID_KEY = "deal_wizard_draft_deal_id"
WIZARD_FEEDBACK_KEY = "deal_wizard_feedback"


def draft_key(field_name: str) -> str:
    return f"{DRAFT_PREFIX}_{field_name}"


def initialize_session_state() -> None:
    """Idempotent. Call once per app entry point."""
    if "deal_profile" not in st.session_state:
        st.session_state["deal_profile"] = DealProfile()
    if PROFILE_VERSION_KEY not in st.session_state:
        st.session_state[PROFILE_VERSION_KEY] = 0
    if WIZARD_STEP_KEY not in st.session_state:
        st.session_state[WIZARD_STEP_KEY] = 0
    if WIZARD_LAST_SEEN_VERSION_KEY not in st.session_state:
        st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = -1


def mark_profile_mutated() -> None:
    """Call after any non-wizard page writes to the canonical deal_profile."""
    st.session_state[PROFILE_VERSION_KEY] = st.session_state.get(PROFILE_VERSION_KEY, 0) + 1


def get_deal_profile() -> DealProfile:
    return st.session_state["deal_profile"]


def reset_deal() -> None:
    """Clears the canonical profile and all wizard draft state."""
    profile_type = type(st.session_state.get("deal_profile", DealProfile()))
    st.session_state["deal_profile"] = profile_type()
    st.session_state[PROFILE_VERSION_KEY] = 0
    st.session_state[WIZARD_STEP_KEY] = 0
    st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = -1
    st.session_state.pop(WIZARD_DRAFT_DEAL_ID_KEY, None)
    st.session_state.pop(WIZARD_FEEDBACK_KEY, None)
    # Clear all draft keys
    keys_to_remove = [k for k in st.session_state if k.startswith(DRAFT_PREFIX + "_")]
    for k in keys_to_remove:
        del st.session_state[k]


def should_reseed_wizard_drafts() -> bool:
    """
    Returns True if an external page has mutated the profile since the wizard
    last seeded its drafts, OR if this is the first time the wizard renders.
    """
    current_version = st.session_state.get(PROFILE_VERSION_KEY, 0)
    last_seen = st.session_state.get(WIZARD_LAST_SEEN_VERSION_KEY, -1)
    current_deal_id = getattr(st.session_state.get("deal_profile"), "id", None)
    seeded_deal_id = st.session_state.get(WIZARD_DRAFT_DEAL_ID_KEY)
    return (current_version != last_seen) or (current_deal_id != seeded_deal_id)


def mark_wizard_synced() -> None:
    """Call after the wizard seeds its draft values."""
    current_version = st.session_state.get(PROFILE_VERSION_KEY, 0)
    current_deal_id = getattr(st.session_state.get("deal_profile"), "id", None)
    st.session_state[WIZARD_LAST_SEEN_VERSION_KEY] = current_version
    st.session_state[WIZARD_DRAFT_DEAL_ID_KEY] = current_deal_id


def go_to_wizard_step(step_index: int, total_steps: int) -> None:
    st.session_state[WIZARD_STEP_KEY] = max(0, min(step_index, total_steps - 1))
```

- [ ] **Step 2: Update session `__init__.py`**

```python
from .state_manager import (
    initialize_session_state, mark_profile_mutated, get_deal_profile,
    reset_deal, should_reseed_wizard_drafts, mark_wizard_synced,
    go_to_wizard_step, draft_key,
    WIZARD_STEP_KEY, WIZARD_FEEDBACK_KEY,
)
__all__ = [...]
```

- [ ] **Step 3: Write unit tests for session manager** (no Streamlit runtime needed – mock `st.session_state` as a dict)

```python
# tests/test_session_manager.py
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

def make_mock_session():
    """Returns a plain dict that acts as st.session_state."""
    return {}

def test_should_reseed_when_profile_version_advanced():
    ...  # set PROFILE_VERSION_KEY to 2, WIZARD_LAST_SEEN to 0, assert should_reseed=True

def test_should_not_reseed_when_versions_match():
    ...  # set both to same value, same deal_id, assert should_reseed=False

def test_reset_deal_clears_all_wizard_keys():
    ...  # seed several draft_ keys, call reset_deal(), assert they are gone
```

- [ ] **Step 4: Run session manager tests**

```bash
python -m pytest tests/test_session_manager.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rental_platform/session/ tests/test_session_manager.py
git commit -m "feat: implement StateManager with profile version tracking"
```

---

## Task 7: Migrate and Fix Deal Verdict Wizard Page

**Files:**
- Create: `rental_platform/pages/deal_verdict_wizard.py`
- Source: `src/deal_verdict_wizard.py` with session management updated to use `StateManager`

The key change is in `_ensure_wizard_state()` (now named `_ensure_wizard_drafts()`):

```python
def _ensure_wizard_drafts(deal_profile) -> None:
    """Reseeds draft values if an external page changed the canonical profile."""
    from rental_platform.session import should_reseed_wizard_drafts, mark_wizard_synced
    if should_reseed_wizard_drafts():
        for field_name, value in _seed_draft_values(deal_profile).items():
            st.session_state[draft_key(field_name)] = value
        st.session_state[WIZARD_FEEDBACK_KEY] = {}
        mark_wizard_synced()
```

All other functions keep their current logic. `show_deal_verdict_wizard` calls `_ensure_wizard_drafts()` instead of `_ensure_wizard_state()`. The "Start Over" handler calls `reset_deal()` from `StateManager` instead of manually clearing individual keys.

- [ ] **Step 1: Create `rental_platform/pages/deal_verdict_wizard.py`** with updated session calls

- [ ] **Step 2: Create `rental_platform/pages/components/verdict_summary.py`** (copy `src/verdict_summary.py`, update imports)

- [ ] **Step 3: Write wizard integration test** to confirm reseed behavior

```python
# tests/test_deal_verdict_wizard.py
# Verify that after an external page increments profile_version,
# _ensure_wizard_drafts() reseeds draft values from the new profile state
```

- [ ] **Step 4: Run wizard tests**

```bash
python -m pytest tests/test_deal_verdict_wizard.py -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rental_platform/pages/deal_verdict_wizard.py rental_platform/pages/components/
git commit -m "fix: wizard reseeds drafts when external page changes canonical profile"
```

---

## Task 8: Migrate Remaining Pages

**Files:**
- Create: `rental_platform/pages/dashboard.py`
- Create: `rental_platform/pages/market_regulatory_intake.py` – add `mark_profile_mutated()` call after profile write
- Create: `rental_platform/pages/acquisition_rehab_modeler.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/capital_markets_simulator.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/underwriting_engine.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/proforma_generator.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/tax_optimizer.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/profit_first_allocator.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/crm_funnel.py` – add `mark_profile_mutated()` call
- Create: `rental_platform/pages/deal_summary_report.py`
- Create: `rental_platform/pages/settings_page.py`

For every page that writes to `deal_profile`, add:
```python
from rental_platform.session import mark_profile_mutated
# ... after profile mutation ...
mark_profile_mutated()
```

- [ ] **Step 1: Create each page file**, updating imports and adding `mark_profile_mutated()` calls

- [ ] **Step 2: Verify no page still imports from `src/` or root-level modules**

```bash
grep -r "from src\." rental_platform/pages/ || echo "clean"
grep -r "from shared\." rental_platform/pages/ || echo "clean"
grep -r "from logic\." rental_platform/pages/ || echo "clean"
```

- [ ] **Step 3: Commit**

```bash
git add rental_platform/pages/
git commit -m "feat: migrate all Streamlit pages to rental_platform.pages"
```

---

## Task 9: Create New App Entry Point

**Files:**
- Create: `app.py` at repository root

```python
# app.py
import streamlit as st
from rental_platform.session import initialize_session_state
from rental_platform.pages.dashboard import show_dashboard
from rental_platform.pages.deal_verdict_wizard import show_deal_verdict_wizard
from rental_platform.pages.market_regulatory_intake import show_market_regulatory_intake
from rental_platform.pages.acquisition_rehab_modeler import show_acquisition_rehab_modeler
from rental_platform.pages.capital_markets_simulator import show_capital_markets_simulator
from rental_platform.pages.underwriting_engine import show_underwriting_engine
from rental_platform.pages.proforma_generator import show_proforma_generator
from rental_platform.pages.tax_optimizer import show_tax_optimizer
from rental_platform.pages.profit_first_allocator import show_profit_first_allocator
from rental_platform.pages.crm_funnel import show_crm_funnel
from rental_platform.pages.deal_summary_report import show_deal_summary_report
from rental_platform.pages.settings_page import show_settings_page


def main():
    st.set_page_config(page_title="Passive Real Estate Underwriting Engine", layout="wide")
    initialize_session_state()

    st.title("Passive Real Estate Underwriting & Evaluation Engine")
    st.markdown(
        "This application provides an institutional-grade evaluation of rental property investments, "
        "removing emotional bias and focusing on the mathematics of the deal."
    )

    pages = {
        "Overview": [st.Page(show_dashboard, title="Dashboard", icon="🏠", default=True)],
        "Deal Analysis": [
            st.Page(show_deal_verdict_wizard, title="Deal Verdict Wizard", icon="⚖️"),
            st.Page(show_market_regulatory_intake, title="Market & Regulatory", icon="📈"),
            st.Page(show_acquisition_rehab_modeler, title="Acquisition & Rehab", icon="🛠️"),
            st.Page(show_capital_markets_simulator, title="Capital Markets", icon="🏦"),
            st.Page(show_underwriting_engine, title="Underwriting Engine", icon="🧮"),
            st.Page(show_proforma_generator, title="Proforma & DCF", icon="📄"),
            st.Page(show_tax_optimizer, title="Tax & Refinance", icon="💰"),
            st.Page(show_profit_first_allocator, title="Profit Allocation", icon="💸"),
        ],
        "Reporting": [st.Page(show_deal_summary_report, title="Deal Summary Report", icon="📊")],
        "Management": [
            st.Page(show_crm_funnel, title="Lead Funnel (CRM)", icon="📧"),
            st.Page(show_settings_page, title="Settings & Integrations", icon="⚙️"),
        ],
    }

    pg = st.navigation(pages)
    pg.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 1: Create root `app.py`**

- [ ] **Step 2: Verify app starts without import errors**

```bash
python -c "import rental_platform; from app import main; print('import OK')"
```

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat: new root entry point importing from rental_platform"
```

---

## Task 10: Migrate Tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_financing_service.py` – migrated from `src/test/test_financing.py`
- Create: `tests/test_underwriting_service.py` – migrated from `src/test/test_underwriting.py`
- Create: `tests/test_verdict_service.py` – migrated from `src/test/test_verdict_workflow.py`
- Create: `tests/test_proforma_service.py`
- Create: `tests/test_rehab_service.py`
- Create: `tests/test_brrrr_service.py`
- Create: `tests/test_tax_service.py`
- Create: `tests/test_profit_first_service.py`
- Create: `tests/test_crm_service.py`

- [ ] **Step 1: Create conftest.py with shared fixtures**

```python
# tests/conftest.py
import pytest
from rental_platform.models import DealProfile

@pytest.fixture
def default_profile():
    return DealProfile()
```

- [ ] **Step 2: For each test file in `src/test/`, create the equivalent in `tests/`**, updating import paths from `src.logic.*` → `rental_platform.services.*` and `shared.models` → `rental_platform.models`

- [ ] **Step 3: Run all migrated tests**

```bash
python -m pytest tests/ -v
```
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add tests/
git commit -m "test: migrate test suite to rental_platform package paths"
```

---

## Task 11: Remove Legacy Root Files

**Files to delete:**
- `models.py` (root) – Pydantic model, superseded by `rental_platform/models/domain.py`
- `deal_verdict_wizard.py` (root) – broken legacy wizard with missing imports
- `state.py` (root) – old session management superseded by `StateManager`
- `calculations.py` (root) – if present, superseded by services
- `rehab.py` (root) – superseded by `rental_platform/services/rehab_service.py`
- `src/` directory – entire old structure no longer needed once all pages and tests pass

- [ ] **Step 1: Verify no active import references legacy files**

```bash
grep -r "from state import\|import state\b\|from models import\|from deal_verdict_wizard import" rental_platform/ app.py tests/ || echo "no references found"
```

- [ ] **Step 2: Delete legacy files**

```bash
rm models.py deal_verdict_wizard.py state.py
rm -f calculations.py rehab.py
rm -rf src/
```

- [ ] **Step 3: Run full test suite to confirm nothing broke**

```bash
python -m pytest tests/ -v
python -c "from app import main; print('app.py import OK')"
```

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "chore: remove legacy src/ directory and root-level stub files"
```

---

## Task 12: End-to-End Validation

- [ ] **Step 1: Run the full test suite**

```bash
python -m pytest tests/ -v --tb=short
```
Expected: All PASS, no import errors

- [ ] **Step 2: Smoke-test app startup**

```bash
streamlit run app.py --server.headless true &
sleep 5
curl -f http://localhost:8501 && echo "app running"
kill %1
```

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: final validation – all tests pass, app starts cleanly"
```
