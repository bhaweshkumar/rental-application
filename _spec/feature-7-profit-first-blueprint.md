# Feature 7: "Profit First" Cash Allocation Blueprint

## 1. Objective

Translate the theoretical underwriting into a strict behavioral bank account schema to guarantee profitability and avoid chronic cash starvation.

## 2. Detailed Specifications

### 2.1. UI Components

- Target Allocation Percentage (TAP) sliders for: Profit (%), Owner's Pay (%), Tax (%), OpEx (%). _Must sum to 100%._

### 2.2. Backend Logic

- Takes the underwritten Year 1 _Gross Revenue_.
- Calculates the exact monthly/bi-weekly dollar sweep required for each of the 5 core depository accounts.
- **OpEx Limit Check:** Compares the dynamically generated "Profit First OpEx limit" against the true calculated OpEx from the Underwriting engine. If the real OpEx is higher than the permitted percentage, it flags the deal as "Operationally Bloated".

### 2.3. Outputs

- A step-by-step banking deposit guide mapping exactly where gross rents go on the 10th and 25th of every month.

## 3. Acceptance Criteria

**Scenario 1: Generating a cash allocation plan for a viable deal.**

- **Given** Year 1 Gross Revenue is $60,000 and true annual OpEx is $25,000.
- **And** I set the OpEx TAP to 65%.
- **When** the system generates the "Profit First" blueprint.
- **Then** the "Profit First OpEx Limit" (Annual) is `$60,000 * 0.65 = $39,000`.
- **And** since the true OpEx ($25,000) is less than the limit, the deal is not flagged.
- **And** the UI should display a guide for depositing the calculated dollar amounts into each account.

**Scenario 2: Flagging a deal as "Operationally Bloated".**

- **Given** Year 1 Gross Revenue is $60,000 and true annual OpEx is $40,000.
- **And** I set the OpEx TAP to 60%.
- **When** the system generates the "Profit First" blueprint.
- **Then** the "Profit First OpEx Limit" (Annual) is `$60,000 * 0.60 = $36,000`.
- **And** since the true OpEx ($40,000) is higher than the permitted limit ($36,000), the system must flag the deal as "Operationally Bloated".
- **And** the UI should display a clear warning message.
