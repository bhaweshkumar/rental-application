Here is the institutional-grade software requirement specification (SRS) for your local real estate underwriting and feasibility application. This system is designed to remove emotional bias, strictly evaluate the mathematics of a deal, and benchmark properties against 2026 macroeconomic standards.

---

## 1. Executive Summary

The **Passive Real Estate Underwriting Engine** is a locally hosted application designed to process property data, evaluate financial viability, and output institutional-grade investment scorecards. The primary objective is to determine if a property meets strict criteria for passive income, DSCR loan qualification, and long-term scaling before capital is deployed.

---

## 2. System Architecture & Tech Stack Recommendations

To ensure the application runs smoothly on your local machine while maintaining the capacity for API integrations, use the following stack:

- **Frontend (UI):** Streamlit (Python) or React.js (for a highly responsive, clean dashboard).
- **Backend (Logic):** Python (Pandas/NumPy) for handling heavy financial calculations, Discounted Cash Flow (DCF) models, and API routing.
- **Database (Local):** SQLite or local JSON storage to save "Deal Profiles" for later comparison.
- **External APIs:** \* Homesage.ai (for automated ARV, comps, and rent projections).
  - PropStream / DealMachine (for property tax, historical data, and seller distress signals).

---

## 3. Module 1: Data Intake & Assumption Interfaces

The user interface must allow for rapid data entry, categorized into distinct input silos.

### 3.1 Property Details Input

- [cite_start]**Address & Asset Type:** Single-family, 2-unit, 4-unit, or commercial multifamily[cite: 85].
- **Square Footage & Year Built.**
- **Market Phase Selection:** Dropdown selecting the current real estate cycle (Recovery, Expansion, Hyper-Supply, Recession).
- [cite_start]**State/Regulatory Tag:** Dropdown to select the state to automatically apply a "Landlord Flexibility" risk score based on typical eviction timelines (e.g., Texas = 21-28 days, Low Risk)[cite: 104].

### 3.2 Acquisition & Rehab Inputs

- [cite_start]**Listing/Purchase Price:** Base acquisition cost[cite: 85].
- **Rehab Estimator (Cost Per Sq Ft Toggle):**
  - [cite_start]Light (Cosmetic/Paint): $15 - $25/sq ft[cite: 96].
  - [cite_start]Medium (Systems/Plumbing): $25 - $50/sq ft[cite: 97].
  - [cite_start]Heavy (Gut/Studs): $65+/sq ft[cite: 98].
  - [cite_start]Contingency Buffer slider (Default 10-15%)[cite: 99].
- [cite_start]**After Repair Value (ARV):** Manual input or API-fetched[cite: 85].

### 3.3 Financing & Leverage Modeler

- **Loan Type Selection:** DSCR, FHA, Conventional, or Creative (Subject-To/Seller Carryback).
- **Down Payment / LTV Ratio:** Default 20-25% for DSCR.
- **Interest Rate & Amortization Period:** Default to 2026 DSCR prime rates (6.125% - 9.125%).

---

## 4. Module 2: The Underwriting Engine (Core Logic)

[cite_start]The backend must compute the "Big Four" deal scorecard metrics strictly adhering to these formulas[cite: 90].

### 4.1 Income & Expense Algorithms

- [cite_start]**Gross Potential Rent (PRI):** Baseline monthly rent $\times$ 12[cite: 86].
- **Effective Gross Income (EGI):** $$EGI = PRI - (PRI \times \text{Vacancy Rate})$$ _(Default vacancy rate to 5%)_
- [cite_start]**Operating Expenses (OpEx):** Sum of Property Taxes, Insurance, Utilities, Repairs/Maintenance, and Property Management Fees[cite: 87].

### 4.2 The "Big Four" Formulas

The application will execute these formulas and color-code the outputs (Green = Pass, Red = Fail) based on institutional benchmarks.

1.  [cite_start]**Net Operating Income (NOI):** The core baseline for valuation[cite: 91].
    $$NOI = EGI - OpEx$$
2.  [cite_start]**Debt Service Coverage Ratio (DSCR):** Assesses default risk[cite: 92].
    $$DSCR = \frac{NOI}{\text{Annual Debt Service}}$$
    - [cite_start]_Benchmark logic:_ If DSCR < 1.20, flag as HIGH RISK[cite: 92]. If > 1.30, flag as OPTIMAL for premium loan pricing.
3.  [cite_start]**Cash-on-Cash Return (CoC):** Assesses capital efficiency[cite: 93].
    $$CoC = \frac{\text{Cash Flow Before Tax}}{\text{Total Initial Cash Invested}}$$
    - [cite_start]_Cash Flow Before Tax calculation:_ $NOI - \text{Annual Debt Service}$[cite: 89].
4.  [cite_start]**Capitalization Rate (Cap Rate):** Unleveraged yield indicator[cite: 94].
    $$Cap Rate = \frac{NOI}{\text{Purchase Price}}$$

---

## 5. Module 3: 3-Year Proforma Output Generator

[cite_start]The application must generate a dynamic multi-year Discounted Cash Flow (DCF) table to forecast operational viability[cite: 83]. This table will apply adjustable "growth drivers" (e.g., 3% annual rent increase, 2% expense inflation).

| Financial Line Item              | Year 1 Projection           | Year 2 Projection | Year 3 Projection |
| :------------------------------- | :-------------------------- | :---------------- | :---------------- |
| **Gross Potential Rent (PRI)**   | Auto-calculated             | $+ 3\%$ Growth    | $+ 3\%$ Growth    |
| **Less: Vacancy & Credit Loss**  | $5\%$ of PRI                | $5\%$ of PRI      | $5\%$ of PRI      |
| **Effective Gross Income (EGI)** | $PRI - \text{Vacancy}$      | Auto-calculated   | Auto-calculated   |
| **Operating Expenses (OpEx)**    | Sum of manual inputs        | $+ 2\%$ Inflation | $+ 2\%$ Inflation |
| **Net Operating Income (NOI)**   | $EGI - OpEx$                | Auto-calculated   | Auto-calculated   |
| **Annual Debt Service (P&I)**    | Fixed per loan terms        | Fixed             | Fixed             |
| **Cash Flow Before Tax**         | $NOI - \text{Debt Service}$ | Auto-calculated   | Auto-calculated   |

---

## 6. Module 4: Deal Scoring & Feasibility Dashboard (UI Layout)

The user interface must be organized into a "cockpit" view for immediate go/no-go decisions.

### Section A: The Deal Scorecard (Top Screen)

- [cite_start]**Visual Gauges:** Four circular gauges displaying CoC Return, Cap Rate, DSCR, and Monthly Cash Flow[cite: 88, 89, 90, 94].
- [cite_start]**Risk Indicator:** A master traffic light (Green/Yellow/Red) based on the combined score of state legislation risk (eviction timelines), market phase, and DSCR strength[cite: 104].

### Section B: The BRRRR / Value-Add Strategy Tracker

- **Equity Capture Display:** Visual bar chart showing `Purchase Price + Rehab` vs. `Appraised ARV`.
- **Cash-Out Refinance Estimator:** Calculates exactly how much capital is trapped or freed if a 75% LTV DSCR refinance is executed post-rehab.

### Section C: "Profit First" Cash Allocation Breakdown

[cite_start]Once a property is deemed feasible, the app outputs an operational blueprint for your bank accounts[cite: 106, 107].

- It takes the Year 1 _Gross Income_ and auto-calculates the exact dollar amounts to sweep monthly into:
  1.  **Profit Account** (e.g., 10%)
  2.  **Owner's Pay Account** (e.g., 10%)
  3.  **Tax Account** (e.g., 15%)
  4.  [cite_start]**OpEx Account** (e.g., 65%) [cite: 108]

## 7. Actionable Next Step

To begin development, export this SRS document and pass it directly to an AI coding assistant (like Cursor or GitHub Copilot) along with the instruction: _"Build a local Streamlit application using Python that perfectly maps to these UI, data structure, and mathematical formula specifications."_
