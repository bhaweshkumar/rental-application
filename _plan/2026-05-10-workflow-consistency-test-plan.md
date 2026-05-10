# Test Plan: Dual-Workflow Data Consistency

## 1. Objective

To verify that data entered and calculated in the "Deal Verdict Wizard" is consistent and synchronized with the "Deep Dive Analysis" pages, and vice-versa. This plan ensures that the shared `deal_profile` object in `st.session_state` functions correctly as the single source of truth across both user workflows, as defined in the `2026-05-10-deal-analysis-workflows.md` plan.

## 2. Scope

### In Scope

- Data synchronization from the Wizard to all relevant Deep Dive pages.
- Data synchronization from Deep Dive pages back to the Wizard and the final `Deal Summary Report`.
- Consistency of key calculated metrics (e.g., DSCR, Cash Flow, Cap Rate, CoC Return) across all views when based on the same input data.
- Verification that changes on one Deep Dive page are reflected on other dependent Deep Dive pages.

### Out of Scope

- Unit testing of individual calculation logic functions (this is covered by `tests/test_*.py` files).
- UI layout, styling, or usability testing.
- Testing of features not part of the two main analysis workflows (e.g., CRM, Settings).

## 3. Prerequisites

- The application is running in a clean session.
- `st.session_state.deal_profile` has been initialized to its default state.
- The tester has a baseline set of property data to use for consistent input across tests (e.g., Purchase Price: $300k, Rent: $2.5k, etc.).

## 4. Test Cases

### Test Case 1: Wizard to Deep Dive Data Flow

- **Description:** Verify that initial data entered into the Deal Verdict Wizard correctly populates the corresponding fields in the Deep Dive pages.
- **Steps:**
  1. Navigate to the `Deal Verdict Wizard`.
  2. Enter the following baseline data:
     - Step 1 (Property): Purchase Price = `$300,000`
     - Step 2 (Rent): Projected Monthly Rent = `$2,500`
     - Step 3 (Financing): Down Payment = `25%`, Interest Rate = `7.0%`, Term = `30` years
     - Step 4 (Expenses): Enter line-item expenses that total `$1,000/month` (`$12,000/year`).
  3. Complete the wizard to get a verdict.
  4. Navigate to **Deep Dive > Acquisition & Value-Add Modeling**.
     - **Expected:** The "Purchase Price" input should display `$300,000`.
  5. Navigate to **Deep Dive > Capital Markets & Leverage Simulator**.
     - **Expected:** The inputs for LTV (`75%`), Interest Rate (`7.0%`), and Term (`30` years) should reflect the wizard's financing inputs.
  6. Navigate to **Deep Dive > The Institutional Underwriting Engine**.
     - **Expected:** The "Projected Monthly Gross Rent" should be `$2,500`. The annual operating expenses should be calculated or displayed as `$12,000`.
- **Success Criteria:** All corresponding fields in the Deep Dive pages are pre-populated with the values entered in the wizard.

### Test Case 2: Deep Dive to Wizard/Summary Data Flow

- **Description:** Verify that data modified in a Deep Dive page updates the shared state and is reflected in the Deal Summary Report and the wizard's calculations.
- **Steps:**
  1. Follow the steps from Test Case 1 to establish a baseline state.
  2. Navigate to **Deep Dive > The Institutional Underwriting Engine** and change "Projected Monthly Gross Rent" from $2,500 to **$2,800** and "Total Monthly Expenses" to **$1,100**.
  3. Navigate to **Deep Dive > Capital Markets & Leverage Simulator** and change "Interest Rate" from 7.0% to **6.5%** and "LTV" to **80%**.
  4. Navigate to the **Deal Summary Report**.
     - **Expected:** All metrics (NOI, Cash Flow, DSCR, etc.) must be recalculated based on the new rent of $2,800 and the new interest rate of 6.5%.
  5. Navigate back to the **Deal Verdict Wizard**.
     - **Expected:** The "Projected Monthly Rent" input should show `$2,800`. The "Interest Rate" should show `6.5%`. The "Total Monthly Expenses" should show `$1,100`. The "Down Payment" slider should show `20%` (100% - 80% LTV). The final verdict must be updated.
- **Success Criteria:** Changes made in Deep Dive pages are correctly reflected in the Deal Summary Report and the Deal Verdict Wizard's state and calculations.

### Test Case 3: Cross-Deep-Dive Page Consistency

- **Description:** Verify that a change on one Deep Dive page is immediately reflected on another dependent Deep Dive page.
- **Steps:**
  1. Start with a clean session.
  2. Navigate to **Deep Dive > Acquisition & Value-Add Modeling**. Set "Purchase Price" to **$400,000** and "Total Rehab Budget" to **$50,000**.
  3. Navigate to **Deep Dive > Capital Markets & Leverage Simulator**.
     - **Expected:** The "Loan Amount" metric must be correctly calculated based on the `$400,000` purchase price and the page's default LTV.
  4. Navigate to **Deep Dive > The Institutional Underwriting Engine**.
     - **Expected:** The "Total Cash Invested" metric must be correctly calculated by summing the down payment (derived from purchase price and LTV) and the `$50,000` rehab budget. This verifies that the rehab budget from the Acquisition page is correctly consumed. The Cash-on-Cash Return calculation should also be present.
- **Success Criteria:** Data flows correctly between dependent pages within the Deep Dive workflow, demonstrating a unified state.

### Test Case 4: Metric Calculation Consistency

- **Description:** Ensure that for an identical set of inputs, key metrics are calculated to the same value regardless of the workflow used for data entry.
- **Steps:**
  1. **Path A (Wizard):**
     - Start with a clean session.
     - Use the `Deal Verdict Wizard` to enter the baseline data from Test Case 1.
     - Record the final calculated values for: `Monthly Cash Flow`, `DSCR`, `Cap Rate`, and `Cash-on-Cash Return`.
  2. **Path B (Deep Dive):**
     - Start a new clean session.
     - Navigate through the `Deep Dive Analysis` pages (1-4) and enter the _exact same_ baseline data from Test Case 1.
     - Navigate to the `Deal Summary Report`.
     - Record the calculated values for: `Monthly Cash Flow`, `DSCR`, `Cap Rate`, and `Cash-on-Cash Return`.
- **Success Criteria:** The recorded metrics from Path A and Path B are identical.
