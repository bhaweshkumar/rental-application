# Feature 4: The Institutional Underwriting Engine (The "Big Four")

## 1. Objective

The core mathematical engine that completely removes emotional bias by calculating strict viability metrics based on operational inputs.

## 2. Detailed Specifications

### 2.1. UI Components

- Inputs for Gross Potential Rent (PRI) and other income (Laundry/Parking).
- Inputs for Operating Expenses (OpEx): Property Taxes, Insurance, Utilities, Maintenance, Property Management Fee (default 8-10%).

### 2.2. Backend Logic (The Formulas)

- **EGI (Effective Gross Income):** `PRI - (PRI * Vacancy Rate)`
- **NOI (Net Operating Income):** `EGI - Total OpEx`
- **DSCR (Debt Service Coverage Ratio):** `NOI / Annual Debt Service`.
  - _Flagging Logic:_ < 1.0 (Fail), 1.0 - 1.19 (High Risk), 1.20+ (Pass), 1.30+ (Optimal/Premium Pricing).
- **CoC (Cash-on-Cash Return):** `(NOI - Annual Debt Service) / Total Initial Cash Invested`.
- **Cap Rate:** `NOI / Purchase Price`.

### 2.3. Outputs

- Color-coded circular gauges or progress bars for the Big Four.

## 3. Acceptance Criteria

**Scenario 1: Underwriting a profitable deal.**

- **Given** a property with $250k price, $62.5k cash invested, $30k annual rent, 5% vacancy, $10k OpEx, and $12k annual debt service.
- **When** the underwriting engine runs the calculations.
- **Then** the NOI should be `$28,500 - $10,000 = $18,500`.
- **And** the DSCR should be `$18,500 / $12,000 = 1.54` (Optimal).
- **And** the CoC Return should be `($18,500 - $12,000) / $62,500 = 10.4%`.
- **And** the Cap Rate should be `$18,500 / $250,000 = 7.4%`.
- **And** the UI should display these metrics in green or "Pass" gauges.

**Scenario 2: Underwriting a high-risk deal.**

- **Given** a property with $350k price, $87.5k cash invested, $32k annual rent, 8% vacancy, $15k OpEx, and $14k annual debt service.
- **When** the underwriting engine runs the calculations.
- **Then** the NOI should be `$29,440 - $15,000 = $14,440`.
- **And** the DSCR should be `$14,440 / $14,000 = 1.03` (High Risk).
- **And** the CoC Return should be `($14,440 - $14,000) / $87,500 = 0.5%`.
- **And** the Cap Rate should be `$14,440 / $350,000 = 4.1%`.
- **And** the UI should display the DSCR gauge in yellow or red ("High Risk").
