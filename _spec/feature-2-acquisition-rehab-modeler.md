# Feature 2: Acquisition & Rehab Modeler (The Value-Add Engine)

## 1. Objective

Standardize rehab cost estimations based on square footage and calculate the After Repair Value (ARV) for BRRRR (Buy, Rehab, Rent, Refinance, Repeat) strategies.

## 2. Detailed Specifications

### 2.1. UI Components

- Inputs: Square Footage, Listing Price, Year Built.
- Toggle/Slider for Rehab Level: Light ($15-$25/sq ft), Medium ($25-$50/sq ft), Heavy/Gut ($65+/sq ft).
- Input for Contractor Contingency (Default: 10-15%).
- Input: After Repair Value (ARV) - manual entry, with an option to fetch estimates via the integrated Data Sourcing module (Feature 9).

### 2.2. Backend Logic

- `Total Rehab Cost = (Sq Ft * Rehab Level Cost) * (1 + Contingency %)`
- `Total Capital Needed = Down Payment + Closing Costs + Total Rehab Cost`
- `Equity Capture = ARV - (Purchase Price + Total Rehab Cost)`

### 2.3. Outputs

- A visual bar chart comparing the "All-In Cost" versus the "ARV", instantly showing "Trapped Equity" vs. "Captured Equity".

## 3. Acceptance Criteria

**Scenario 1: Calculating costs for a light cosmetic rehab.**

- **Given** a 1,500 sq ft property with a $200,000 list price, $50k down, $5k closing costs, and a $250,000 ARV.
- **And** I select the "Light" rehab level at $20/sq ft with a 10% contingency.
- **When** the system calculates the costs.
- **Then** the "Total Rehab Cost" should be `(1500 * 20) * 1.10 = $33,000`.
- **And** the "Total Capital Needed" should be `$50,000 + $5,000 + $33,000 = $88,000`.
- **And** the "Equity Capture" should be `$250,000 - ($200,000 + $33,000) = $17,000`.
- **And** the UI should display a bar chart comparing the "All-In Cost" ($233,000) to the "ARV" ($250,000).

**Scenario 2: Calculating costs for a heavy gut rehab.**

- **Given** a 2,000 sq ft property with a $150,000 list price, $37.5k down, $4k closing costs, and a $300,000 ARV.
- **And** I select the "Heavy/Gut" rehab level at $70/sq ft with a 15% contingency.
- **When** the system calculates the costs.
- **Then** the "Total Rehab Cost" should be `(2000 * 70) * 1.15 = $161,000`.
- **And** the "Total Capital Needed" should be `$37,500 + $4,000 + $161,000 = $202,500`.
- **And** the "Equity Capture" should be `$300,000 - ($150,000 + $161,000) = -$11,000` (Trapped Equity).
- **And** the UI should display a bar chart showing the "All-In Cost" ($311,000) is higher than the "ARV" ($300,000).
