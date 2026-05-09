# Institutional Underwriting Engine - Development Plan

## 1. Guiding Principles

This document outlines the development plan for the Passive Real Estate Underwriting Engine. All development will adhere to the following principles:

- **Test-Driven Development (TDD):** All business logic will be developed test-first. We write a failing test, write the code to make it pass, and then refactor.
- **Separation of Concerns (SOLID):**
  - **Logic:** Core financial calculations will be in pure, testable Python functions/modules (e.g., `src/logic/`).
  - **UI:** Streamlit pages (`src/`) will handle user input and display data, but will not contain complex business logic.
  - **Data:** All state will be managed through structured `dataclasses` in `src/shared/models.py`.
- **Don't Repeat Yourself (DRY):** Common calculations and constants will be centralized.
- **You Ain't Gonna Need It (YAGNI):** We will build the simplest thing that works to meet the current feature specification, avoiding premature optimization or features.

---

## 2. Feature Implementation Plan

### Feature 1: Market & Regulatory Intake

- **Status:** 90% Complete.
- **Next Steps:**
  - Expand `LANDLORD_FLEXIBILITY_RISK` in `src/shared/constants.py` with more states as per research.

### Feature 2: Acquisition & Rehab Modeler

- **Status:** 60% Complete. The UI is present, but the logic is not fully separated or tested.
- **Objective:** Standardize rehab cost estimation and analyze value-add potential.
- **TDD Plan:**
  1.  **Create `src/logic/brrrr.py`:** This new module will house the business logic.
  2.  **Write Tests (`tests/test_brrrr.py`):**
      - Create a test for a new function: `calculate_brrrr_metrics(purchase_price, total_rehab_budget, arv, refi_ltv_pct)`.
      - This function will return a dataclass or dictionary containing `all_in_cost`, `equity_capture`, `refi_loan_amount`, and `cash_out_proceeds`.
      - Test positive equity capture, negative equity capture (trapped equity), and zero cash-out scenarios.
  3.  **Implement `calculate_brrrr_metrics`:** Write the code to make the tests pass.
  4.  **Refactor UI (`acquisition_rehab_modeler.py`):**
      - Import and call the new `calculate_brrrr_metrics` function.
      - The UI section "BRRRR / Value-Add Strategy Tracker" will now be powered by this tested function, ensuring its accuracy.

### Feature 3: Capital Markets & Leverage Simulator

- **Status:** Not Started.
- **Objective:** Model different loan types (Conventional, DSCR) to determine financing costs, down payment, and total cash needed.
- **TDD Plan:**
  1.  **Create `src/logic/financing.py`:**
  2.  **Write Tests (`tests/test_financing.py`):**
      - Test `calculate_loan_details(purchase_price, ltv_pct, closing_costs_pct)` -> returns `(loan_amount, down_payment, closing_costs)`.
      - Test `calculate_monthly_payment(loan_amount, annual_interest_rate, term_years)` -> returns `monthly_p_and_i`. Use a known online calculator to verify the formula.
  3.  **Implement Logic:** Write the code in `src/logic/financing.py` to pass the tests.
  4.  **Update Data Model (`shared/models.py`):**
      - Create a `CapitalMarketsDetails` dataclass with fields like `loan_type`, `ltv_pct`, `interest_rate`, `term_years`, `closing_costs_pct`, `loan_amount`, `down_payment`, `monthly_payment`, `annual_debt_service`.
      - Add `capital_markets_details: CapitalMarketsDetails` to the `DealProfile` dataclass.
  5.  **Build UI (`capital_markets_simulator.py`):**
      - Create a new page file.
      - Add inputs for LTV, interest rate, and term.
      - Call the tested logic functions to calculate and display the loan details.
      - On save, populate the `CapitalMarketsDetails` model in the session state.

### Feature 4: The Institutional Underwriting Engine

- **Status:** Not Started.
- **Objective:** Calculate the "Big Four" institutional metrics: NOI, Cap Rate, DSCR, and Cash-on-Cash Return.
- **TDD Plan:**
  1.  **Create `src/logic/underwriting.py`:**
  2.  **Write Tests (`tests/test_underwriting.py`):**
      - Test `calculate_noi(gross_rent, vacancy_pct, operating_expenses)`
      - Test `calculate_cap_rate(noi, purchase_price)`
      - Test `calculate_dscr(noi, annual_debt_service)` (will use output from Feature 3 logic).
      - Test `calculate_cash_on_cash(noi, annual_debt_service, down_payment, closing_costs, rehab_budget)` (will use outputs from Features 2 & 3).
  3.  **Implement Logic:** Write the code in `src/logic/underwriting.py`.
  4.  **Update Data Model (`shared/models.py`):**
      - Create `UnderwritingDetails` dataclass for inputs (`gross_rent`, `opex_pct`, etc.) and outputs (`noi`, `cap_rate`, `dscr`, `coc_return`).
      - Add to `DealProfile`.
  5.  **Build UI (`underwriting_engine.py`):**
      - Create a new page file.
      - Add inputs for Gross Rent and Operating Expenses (as a % of rent or fixed value).
      - Pull `purchase_price`, `debt_service`, and `total_cash_invested` from the other data models in the `DealProfile`.
      - Display the "Big Four" in a clear scorecard using `st.metric`.

### Feature 5: 3-Year Proforma & DCF Generator

- **Status:** Not Started.
- **Objective:** Project income, expenses, and cash flow over a multi-year holding period.
- **TDD Plan:**
  1.  **Create `src/logic/proforma.py`:**
  2.  **Write Tests (`tests/test_proforma.py`):**
      - Test `generate_proforma_line_items(deal_profile, growth_assumptions)` -> returns a list of dictionaries, one for each year of the proforma, containing projected GPR, EGI, OpEx, NOI, and CFBT.
      - Test with 0% growth, positive growth, and negative growth.
  3.  **Implement Logic:** Write the proforma generation loop.
  4.  **Update Data Model (`shared/models.py`):**
      - Create `ProformaAssumptions` dataclass (`rent_growth_pct`, `expense_growth_pct`, `holding_period`).
      - Add to `DealProfile`.
  5.  **Build UI (`proforma_generator.py`):**
      - Create a new page file.
      - Add sliders for rent and expense growth assumptions.
      - Call the tested logic and display the resulting proforma in a `st.dataframe`.

### Future Features (Post-Core Engine)

The following features will be planned in detail after the core underwriting engine (Features 1-5) is complete and stable. This aligns with the YAGNI principle.

- **Feature 6: BRRRR Refinance & Tax Optimization:**
  - **Objective:** Model cost segregation and bonus depreciation.
  - **High-Level Plan:** Create a `tax.py` logic module to calculate depreciation schedules.

- **Feature 7: 'Profit First' Cash Allocation:**
  - **Objective:** Model the behavioral cash management system.
  - **High-Level Plan:** Create a `profit_first.py` logic module to calculate cash sweeps based on Target Allocation Percentages (TAPs).

- **Feature 8: Automated Lead Funnel (CRM):**
  - **Objective:** Provide a UI to track deals.
  - **High-Level Plan:** This is a larger feature that may involve a database or flat-file storage. Will require its own detailed spec.

- **Feature 9: Data Integration & Settings:**
  - **Objective:** Integrate with third-party APIs (e.g., for ARV estimates, rent comps).
  - **High-Level Plan:** Will involve creating an API client service layer and handling API keys securely.

---

## 3. Execution Order

We will proceed in the following order to ensure dependencies are met:

1.  **Refactor Feature 2** (Acquisition & Rehab)
2.  **Build Feature 3** (Capital Markets)
3.  **Build Feature 4** (Underwriting Engine)
4.  **Build Feature 5** (Proforma Generator)

This order ensures that the data required by each feature is made available by the preceding one (e.g., Feature 4 needs `annual_debt_service` from Feature 3).
