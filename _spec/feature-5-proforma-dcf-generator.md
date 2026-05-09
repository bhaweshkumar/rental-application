# Feature 5: 3-Year Proforma & Discounted Cash Flow (DCF) Generator

## 1. Objective

Project long-term performance and account for inflation, rent growth, and asset appreciation to validate intrinsic value.

## 2. Detailed Specifications

### 2.1. UI Components

- Settings panel for "Growth Drivers": Annual Rent Increase % (Default 3%), Annual Expense Inflation % (Default 2%).
- A clean data table (using Streamlit `st.dataframe`) displaying Years 1, 2, and 3.

### 2.2. Backend Logic

- Iteratively calculates Income and Expenses year-over-year.
- **Year N Rent:** `Year N-1 Rent * (1 + Rent Growth %)`
- **Year N OpEx:** `Year N-1 OpEx * (1 + Expense Inflation %)`
- **IRR Calculation:** Synthesizes periodic cash flows over a projected 5-to-10 year hold, factoring in a terminal sale price (reversion value) based on the exit Cap Rate.

### 2.3. Outputs

- Multi-year spreadsheet-style Proforma.

## 3. Acceptance Criteria

**Scenario 1: Generating a 3-year proforma with default growth drivers.**

- **Given** Year 1 projections: Gross Rent of $120,000 and OpEx of $40,000.
- **And** default growth drivers are 3% rent increase and 2% expense inflation.
- **When** the 3-year proforma is generated.
- **Then** the proforma table should display for Year 2: Gross Rent of $123,600 and OpEx of $40,800.
- **And** for Year 3: Gross Rent of $127,308 and OpEx of $41,616.
- **And** NOI and Cash Flow should be recalculated for each year.

**Scenario 2: Generating a proforma with custom growth drivers.**

- **Given** the same Year 1 projections as Scenario 1.
- **And** I set custom growth drivers to 5% rent increase and 3% expense inflation.
- **When** the 3-year proforma is generated.
- **Then** the proforma table should display for Year 2: Gross Rent of $126,000 and OpEx of $41,200.
- **And** the values for Year 3 should be calculated based on the Year 2 values and the custom growth drivers.
