# Deal Verdict Wizard — Session Persistence Fix and Integration Tests

**Goal:** Fix data loss for Rent, Financing, and Expenses wizard steps when the user navigates back and forth. Add a comprehensive integration test that exercises real next/back navigation across all steps and asserts full data survival on the Verdict step.

---

## Root Cause Analysis

### What is already fixed

`_sync_draft_to_profile()` now skips draft keys absent from `st.session_state`, and `_restore_missing_draft_keys()` refills any absent keys from the canonical profile after the sync. This prevents Property (Step 1) data from being corrupted when Streamlit's widget-state cleanup removes Step 1 widget keys while the user is on a later step.

### Why subsequent steps still fail

**Problem 1 — `value=` + `key=` dual specification on every widget helper.**

`_draft_number_input()`, `_draft_slider()`, and `_draft_text()` all pass both `key=draft_key(field)` and `value=st.session_state.get(dk, minimum)`. Streamlit's documented guidance is that setting a widget value through Session State while also using the widget's `value` parameter is not the recommended pattern, and it triggers a warning. In practice the widget can end up using the widget-level default rather than the session-state-restored value when the two compete, which means `_restore_missing_draft_keys()` may restore the correct value but the widget immediately overwrites it with `minimum`.

**Problem 2 — No `on_change` callback; profile update is deferred to the next render.**

Currently the profile is only updated at the very beginning of each render inside `_sync_draft_to_profile()`. If the user changes a widget and then immediately clicks the tab navigation bar before Streamlit can commit the widget interaction into a new render, the change is never captured. More critically, for Rent/Financing/Expenses steps the profile values remain at their previous state until the next render syncs them, but Streamlit may have already cleaned up the draft keys by then, so that sync silently does nothing.

**Net effect:** Rent, Financing, and Expenses input values are lost whenever the user jumps across steps using the top navigation tabs rather than the sequential Continue/Back buttons, and even sequential navigation can lose data on slow networks or fast clicks.

---

## Proposed Changes

### Change 1 — Remove `value=` from keyed widget helpers

In `rental_platform/pages/deal_verdict_wizard.py`, update `_draft_text()`, `_draft_number_input()`, and `_draft_slider()` to use **only** `key=` for the widget binding.

The correct Streamlit pattern is:
```python
# Initialize session_state key BEFORE the widget renders (already done by
# _restore_missing_draft_keys called from _refresh_wizard_profile).
# Then render the widget without value= so session_state is the single
# source of truth.
st.number_input(label, min_value=minimum, step=step, key=dk)
```

The `_restore_missing_draft_keys()` call that runs before any widgets are rendered ensures `dk` is always present in session state by the time the widget fires, so removing `value=` is safe.

### Change 2 — Add `on_change` callbacks to commit field changes immediately into `deal_profile`

Each wizard widget gets an `on_change` callback that reads the widget's new value from `st.session_state[dk]` and writes it directly into the canonical `deal_profile`, then calls `refresh_deal_calculations()`.

Introduce a single field-write helper to centralise the field→profile mapping:

```python
def _write_field_to_profile(field_name: str, deal_profile) -> None:
    """Reads a single draft key and writes it into the canonical profile."""
    dk = draft_key(field_name)
    if dk not in st.session_state:
        return
    # ... same field→profile mapping as _sync_draft_to_profile, but for one field
```

Then build a per-field callback factory:

```python
def _on_field_change(field_name: str) -> None:
    """on_change handler: commits the single changed field then recalculates."""
    deal_profile = st.session_state["deal_profile"]
    _write_field_to_profile(field_name, deal_profile)
    refresh_deal_calculations(deal_profile)
```

Widget calls become:
```python
st.number_input(label, min_value=minimum, step=step, key=dk,
                on_change=_on_field_change, args=(field_name,))
```

After this change the expected data flow is:

1. Draft key initialized from profile by `_restore_missing_draft_keys()` before widget renders.
2. User edits widget → `on_change` fires → changed value committed to profile immediately → calculations refreshed.
3. On any subsequent render, `_sync_draft_to_profile()` acts as a safety net for any keys that survived; `_restore_missing_draft_keys()` refills any that Streamlit cleaned up.

### Change 3 — Retain `_sync_draft_to_profile` and `_restore_missing_draft_keys` as safety nets

No removal; they continue to handle direct step jumps and reruns where `on_change` may not have fired (e.g. read-only display of previous step values). Their role is now defensive rather than primary.

### Change 4 — Add a wizard integration test runner

Create `tests/wizard_runner.py` — a minimal Streamlit script that `AppTest` can load:

```python
import streamlit as st
from rental_platform.session import initialize_session_state
from rental_platform.pages.deal_verdict_wizard import show_deal_verdict_wizard

initialize_session_state()
show_deal_verdict_wizard()
```

This avoids pulling in the full `app.py` multi-page navigation tree and gives the integration tests a stable entry point.

### Change 5 — Add `tests/test_wizard_integration.py`

Use `streamlit.testing.v1.AppTest` to run the wizard through real widget interactions.

**Test cases required:**

1. **Forward happy path** — Fill all required fields in sequence (Property → Rent → Financing → Expenses) using the Continue buttons; verify Verdict step shows non-zero cash flow, DSCR, and cap rate.

2. **Rent survives forward then back** — Enter rent on Step 2, proceed to Financing, navigate back to Rent; assert widget value and `deal_profile.verdict_inputs.monthly_rent` both retain the entered value.

3. **Financing survives forward then back** — Enter interest rate on Step 3, proceed to Expenses, navigate back to Financing; assert widget value and `deal_profile.capital_markets_details.interest_rate_pct` both retain the entered value.

4. **Expenses survives forward then back** — Enter property taxes on Step 4, navigate to Verdict, navigate back to Expenses; assert widget value and `deal_profile.expense_line_items.annual_property_taxes` both retain the entered value.

5. **Repeated back-and-forth stress test** — Fill all four input steps, then navigate: Verdict → Expenses → Financing → Rent → Property → Rent → Financing → Expenses → Verdict. After this sequence assert that all entered values are still in `deal_profile` and that the Verdict step reports a calculated (non-zero) result derived from all four steps.

6. **Direct tab-jump to Financing without filling Property** — Click the Financing tab directly from the initial state; assert that the "Set the asking price first" warning appears and no crash occurs.

Integration assertions must check **both** `deal_profile` fields and, where practical, the widget `value` visible in `AppTest` so regressions in either the UI layer or the data layer are caught.

---

## Files to Create or Modify

| File | Change |
|---|---|
| `rental_platform/pages/deal_verdict_wizard.py` | Remove `value=` from widget helpers; add `_write_field_to_profile()`; add `on_change` to all widgets |
| `tests/wizard_runner.py` | New — minimal `AppTest` entry point |
| `tests/test_wizard_integration.py` | New — six integration test scenarios |

---

## Validation

Run in order:

1. `pytest tests/test_deal_verdict_wizard.py -v` — existing unit tests must all still pass.
2. `pytest tests/test_wizard_integration.py -v` — all six integration scenarios must pass.
3. `pytest tests/ --ignore=tests/test_workflow_consistency.py --ignore=tests/test_data_integration.py -q` — broader suite must show no new failures.

---

## Implementation Notes

- Integration tests must interact through actual wizard buttons and sliders (not by mutating `st.session_state` directly) because the bug is in the real widget/render lifecycle. Direct session-state manipulation would bypass the issue entirely.
- The stress test (test case 5) should navigate across at least three full round trips before asserting so that the fix is verified under the same conditions the user actually reported.
- The `on_change` callback signature uses `args=(field_name,)` rather than a closure to keep the callback picklable should Streamlit serialization be enabled.
- `_draft_select()` uses the `index=` pattern rather than `value=` and does not have a `minimum` sentinel; it must be updated to pass `on_change` but its initialization logic can remain as-is.
