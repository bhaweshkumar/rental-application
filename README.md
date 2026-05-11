# Passive Real Estate Underwriting & Evaluation Engine

An institutional-grade, locally hosted Streamlit application designed to evaluate rental property investments for passive investors. The system removes emotional bias by strictly evaluating the mathematics of a deal — benchmarked against 2026 macroeconomic standards, regulatory environments, and advanced financing structures (DSCR, BRRRR).

---

## Features

The application is organized into four navigation groups:

### Overview
- **Dashboard** — Cockpit-style summary of all active deal metrics and portfolio state.

### Deal Analysis
- **Deal Verdict Wizard** — Step-by-step guided workflow that produces a Go/No-Go verdict with a color-coded risk scorecard.
- **Market & Regulatory** — Select state and market cycle phase; applies automatic landlord-flexibility risk scores based on eviction timelines.
- **Acquisition & Rehab Modeler** — Estimate rehab costs by scope (Light / Medium / Heavy), compute all-in acquisition cost, and model BRRRR equity capture.
- **Capital Markets Simulator** — Model DSCR, FHA, Conventional, and Creative (Subject-To / Seller Carryback) loan structures to determine financing cost and total cash required.
- **Underwriting Engine** — Calculates the "Big Four" institutional metrics: NOI, Cap Rate, DSCR, and Cash-on-Cash Return, with pass/fail benchmarks.
- **Proforma & DCF** — Generates a multi-year Discounted Cash Flow (DCF) proforma with configurable rent growth and expense inflation assumptions.
- **Tax & Refinance** — Models cost segregation, bonus depreciation schedules, and cash-out refinance proceeds post-rehab.
- **Profit Allocation** — Implements the "Profit First" cash-management system, auto-calculating monthly account sweeps from gross income.

### Reporting
- **Deal Summary Report** — Consolidated, printable deal scorecard aggregating all analysis modules.

### Management
- **Lead Funnel (CRM)** — Pipeline view for tracking prospective deals, with webhook support for Make.com / Zapier integrations.
- **Settings & Integrations** — Configure API keys and third-party data-source integrations (ARV, rent comps, property data).

---

## Technology Stack

| Layer | Technology |
|---|---|
| UI / Frontend | Streamlit 1.50 |
| Financial Logic | Python 3.9, NumPy 2.0, NumPy-Financial 1.0, Pandas 2.3 |
| Charting | Altair 5.5 |
| Testing | Pytest 8.4 |
| Data Validation | jsonschema 4.25 |
| Storage | Local JSON (settings & deal profiles) |

---

## Project Structure

```
rental-application/
├── app.py                          # Streamlit entry point
├── rental_platform/
│   ├── constants/
│   │   └── real_estate.py          # Landlord flexibility scores, market phase definitions
│   ├── models/
│   │   └── domain.py               # DealProfile and all domain dataclasses
│   ├── pages/                      # One module per Streamlit page
│   │   ├── dashboard.py
│   │   ├── deal_verdict_wizard.py
│   │   ├── market_regulatory_intake.py
│   │   ├── acquisition_rehab_modeler.py
│   │   ├── capital_markets_simulator.py
│   │   ├── underwriting_engine.py
│   │   ├── proforma_generator.py
│   │   ├── tax_optimizer.py
│   │   ├── profit_first_allocator.py
│   │   ├── deal_summary_report.py
│   │   ├── crm_funnel.py
│   │   └── settings_page.py
│   ├── services/                   # Pure business-logic modules (no Streamlit)
│   │   ├── brrrr_service.py
│   │   ├── financing_service.py
│   │   ├── underwriting_service.py
│   │   ├── proforma_service.py
│   │   ├── tax_service.py
│   │   ├── profit_first_service.py
│   │   ├── verdict_service.py
│   │   ├── crm_service.py
│   │   ├── data_integration_service.py
│   │   └── settings_service.py
│   ├── session/
│   │   └── state_manager.py        # Centralized Streamlit session-state initialization
│   └── utils/
│       └── coercion.py             # Type-safe input helpers
├── tests/                          # Pytest test suite (mirrors services/)
├── _spec/                          # Software Requirement Specifications (SRS)
├── _requirements/                  # Original product requirements
├── _plan/                          # Implementation planning documents
└── research/                       # Market research and reference material
```

---

## Setup

### Prerequisites
- Python 3.9+
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd rental-application
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install streamlit pandas numpy numpy-financial altair pytest jsonschema
   ```

---

## Running the Application

```bash
source .venv/bin/activate
streamlit run app.py
```

The app will open at `http://localhost:8501` in your browser.

---

## Running Tests

```bash
source .venv/bin/activate
pytest tests/
```

All business logic in `rental_platform/services/` has corresponding tests in `tests/`.

---

## Development Principles

- **Test-Driven Development (TDD):** All business logic is developed test-first.
- **Separation of Concerns:** Pages handle UI only; services contain all financial logic; domain models hold all state.
- **DRY:** Common calculations and constants are centralized in `constants/` and `utils/`.
- **YAGNI:** The simplest solution that satisfies the current specification is always preferred.

---

## Core Financial Formulas

| Metric | Formula |
|---|---|
| Effective Gross Income (EGI) | `GPR − (GPR × Vacancy Rate)` |
| Net Operating Income (NOI) | `EGI − Operating Expenses` |
| Debt Service Coverage Ratio (DSCR) | `NOI ÷ Annual Debt Service` _(≥1.20 required; ≥1.30 optimal)_ |
| Cash-on-Cash Return (CoC) | `Cash Flow Before Tax ÷ Total Cash Invested` |
| Cap Rate | `NOI ÷ Purchase Price` |
| Cash Flow Before Tax (CFBT) | `NOI − Annual Debt Service` |
