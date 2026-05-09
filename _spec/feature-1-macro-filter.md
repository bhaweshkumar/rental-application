# Feature 1: Market & Regulatory Intake (The Macro Filter)

## 1. Objective

Eliminate non-viable properties before financial underwriting begins by assessing macroeconomic and legislative risks.

## 2. Detailed Specifications

### 2.1. UI Components

- Input fields for Property Address, Asset Type (Single Family, 2-Unit, 4-Unit, Commercial).
- Dropdown for "Real Estate Market Phase" (Recovery, Expansion, Hyper-Supply, Recession).
- Dropdown for "State".

### 2.2. Backend Logic & Data Dictionary

- **Legislative Risk Score:** Maps the selected State to an internal dictionary defining landlord friendliness.
  - _Low Risk (Score 1):_ Texas, Indiana, Georgia (Evictions < 30 days).
  - _High Risk (Score 5):_ California, New Jersey, New York (Rent control, strict eviction laws).
- **Market Phase Adjuster:** If "Hyper-Supply" or "Recession" is selected, the backend automatically increases the projected Vacancy Rate default from 5% to 8-10%.

### 2.3. Outputs

- A "Macro Viability Rating" (Pass/Warning/Fail) displayed at the top of the deal profile.

## 3. Acceptance Criteria

**Scenario 1: Evaluating a property in a landlord-friendly state during an expansion phase.**

- **Given** I have entered a property address and selected "Expansion" and "Texas".
- **When** the system processes the inputs.
- **Then** the backend should assign a "Legislative Risk Score" of 1 (Low Risk).
- **And** the default Vacancy Rate should remain at its standard value (e.g., 5%).
- **And** the UI should display a "Macro Viability Rating" of "Pass".

**Scenario 2: Evaluating a property in a tenant-friendly state during a recession.**

- **Given** I have entered a property address and selected "Recession" and "California".
- **When** the system processes the inputs.
- **Then** the backend should assign a "Legislative Risk Score" of 5 (High Risk).
- **And** the backend should automatically adjust the default Vacancy Rate to a value between 8% and 10%.
- **And** the UI should display a "Macro Viability Rating" of "Fail" or "Warning".

**Scenario 3: Market phase adjustment for vacancy rate.**

- **Given** a property is being evaluated.
- **When** I select "Hyper-Supply" or "Recession" as the "Real Estate Market Phase".
- **Then** the application's default Vacancy Rate for calculations should increase from 5% to a value between 8% and 10%.
- **When** I select "Recovery" or "Expansion", the default Vacancy Rate should be 5%.
