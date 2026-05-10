# Passive Rental Deal Verdict Workflow Plan

## Summary
Build a new `Deal Verdict Wizard` as the primary UI path in the Streamlit app. Its job is to answer one question for a day-job investor: is this property priced well enough to be a passive long-term rental that clears at least `$300/month` after mortgage and core operating costs. The workflow should replace the current module-first experience as the default entry path, while keeping the existing feature pages available as expert/detail views.

## Key Changes
- Add a new top-level page/component, `src/deal_verdict_wizard.py`, and make it the first/default navigation option from `src/app.py`.
- Use a 5-step guided flow with progressive disclosure:
  1. `Property`: address, asset type, state, sq ft, year built, asking price.
  2. `Rent`: expected monthly rent, optional other monthly income, vacancy assumption.
  3. `Financing`: loan type, down payment or LTV, rate, term, closing costs.
  4. `Expenses`: line-item operating costs, not a single OpEx percent.
  5. `Verdict`: monthly cash flow after debt, DSCR, cap rate, cash-on-cash return, total cash needed, plus pass/fail reasons.
- Treat this as a `long-term rental only` workflow in v1.
- Make the verdict `return-based`, not heuristic-only.
- Use `cash-flow-first` verdict rules:
  - `Pass`: monthly free cash flow `>= $300` and DSCR `>= 1.20`.
  - `Caution`: positive cash flow but below `$300`, or DSCR between `1.00` and `1.19`.
  - `Fail`: negative monthly cash flow, DSCR `< 1.00`, or required inputs missing.
- Extend the data model in `src/logic/models.py` so the wizard can store:
  - Line-item expense inputs.
  - A computed monthly cash flow value.
  - A verdict status and reason list.
  - Wizard progress/current step in session state.
- Reuse existing underwriting and financing logic where possible, but add a dedicated verdict-layer function that converts computed metrics into `Pass / Caution / Fail` plus human-readable reasons.
- Update the summary experience so the final wizard screen becomes the single-deal report for this property.

## Public Interfaces / Types
- Add a `VerdictInputs` structure for wizard-only fields.
- Add an `ExpenseLineItems` structure with explicit annual/monthly expense fields.
- Add a `VerdictOutputs` structure with:
  - `monthly_cash_flow`
  - `dscr`
  - `cap_rate`
  - `cash_on_cash_return`
  - `total_cash_required`
  - `verdict_status`
  - `verdict_reasons`

## Test Plan
- Verify the wizard blocks progression when required fields for the current step are missing.
- Verify line-item expenses aggregate correctly into annual operating expenses.
- Verify monthly cash flow uses rent, vacancy, expenses, and debt service consistently.
- Verify verdict thresholds exactly at boundaries.
- Verify existing underwriting calculations still render consistent cap rate, DSCR, and cash-on-cash values when fed wizard data.
- Verify the final report shows both the verdict and the reasons, not just raw metrics.

## Assumptions
- v1 is manual-entry only.
- The workflow is for one property at a time.
- The main user is a passive investor with a day job, so the UX should favor fast go/no-go clarity over institutional depth on the first pass.
