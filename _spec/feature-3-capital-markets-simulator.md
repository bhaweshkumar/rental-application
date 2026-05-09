# Feature 3: Capital Markets & Leverage Simulator

## 1. Objective

Model different financing scenarios to determine the impact on cash flow, heavily emphasizing the infinite-scaling DSCR loan method.

## 2. Detailed Specifications

### 2.1. UI Components

- Radio buttons for Loan Type: FHA (3.5% down, owner-occ), Conventional (15-25% down, DTI constrained), DSCR (15-25% down, no DTI limit), Creative (Subject-To/Seller Carryback).
- Sliders for Interest Rate (e.g., 6.125% - 9.125% for DSCR), LTV Ratio, and Amortization Period (usually 360 months).

### 2.2. Backend Logic

- Utilizes numpy's financial functions (`numpy_financial.pmt`) to calculate monthly Principal and Interest (P&I).
- **Rule Enforcement:** If FHA is selected, trigger a UI warning regarding the 1-year owner-occupancy requirement and strict property condition standards.

### 2.3. Outputs

- Exact monthly Debt Service calculation fed directly into the Underwriting Engine.

## 3. Acceptance Criteria

**Scenario 1: Calculating debt service for a DSCR loan.**

- **Given** I am evaluating a property with a purchase price of $300,000.
- **And** I select "DSCR" as the Loan Type, with 75% LTV, 7.0% Interest Rate, and 360-month amortization.
- **When** the system calculates the debt service.
- **Then** the backend should use a financial library to calculate the monthly P&I payment (approx. $1,496.93).
- **And** this value should be passed to the underwriting engine.

**Scenario 2: Selecting an FHA loan triggers a UI warning.**

- **Given** I am on the financing input screen.
- **When** I select "FHA" as the Loan Type.
- **Then** the UI must display a clear and visible warning message.
- **And** the warning message should state the 1-year owner-occupancy requirement and mention that the property must meet strict condition standards.
