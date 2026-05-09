# Feature 6: BRRRR Refinance & Tax Optimization Modeler

## 1. Objective

Simulate the back-end of the BRRRR strategy to see how much tax-free capital can be pulled out post-rehab.

## 2. Detailed Specifications

### 2.1. UI Components

- "Execute Cash-Out Refinance" toggle.
- Inputs: Refinance LTV (Default 75%), Refinance Interest Rate, Timeline (Months to stabilization).

### 2.2. Backend Logic

- `New Loan Amount = ARV * Refinance LTV`
- `Cash Pulled Out = New Loan Amount - Existing Original Loan Payoff - Refinance Closing Costs`
- `Capital Left in Deal = Total Initial Cash Invested - Cash Pulled Out`
- _Infinite Return Check:_ If `Capital Left in Deal` <= 0, flag the Cash-on-Cash return as "Infinite (∞)".

### 2.3. Outputs

- A summary module titled "Wealth Harvesting" showing exactly how much capital is recouped to deploy into the next asset.

## 3. Acceptance Criteria

**Scenario 1: Successful cash-out refinance achieving an infinite return.**

- **Given** a deal with ARV of $300k, original loan payoff of $150k, and initial cash invested of $55k.
- **And** I execute a cash-out refinance at 75% LTV with $5k in closing costs.
- **When** the system calculates the outcome.
- **Then** the "New Loan Amount" should be $225,000.
- **And** the "Cash Pulled Out" should be `$225,000 - $150,000 - $5,000 = $70,000`.
- **And** the "Capital Left in Deal" should be `$55,000 - $70,000 = -$15,000`.
- **And** the system should flag the deal's CoC return as "Infinite (∞)".

**Scenario 2: Cash-out refinance where capital remains in the deal.**

- **Given** a deal with ARV of $250k, original loan payoff of $160k, and initial cash invested of $60k.
- **And** I execute a cash-out refinance at 70% LTV with $4k in closing costs.
- **When** the system calculates the outcome.
- **Then** the "New Loan Amount" should be $175,000.
- **And** the "Cash Pulled Out" should be `$175,000 - $160,000 - $4,000 = $11,000`.
- **And** the "Capital Left in Deal" should be `$60,000 - $11,000 = $49,000`.
