# Dual-Workflow Analysis Structure

## Summary

This plan formalizes the application's structure into two distinct, parallel user workflows for deal analysis:

1.  **The Deal Verdict Wizard**: A streamlined path for quick, high-level go/no-go decisions.
2.  **The Deep Dive Analysis**: A comprehensive, step-by-step path for in-depth, institutional-grade underwriting.

This clarifies the purpose of the pages under the "Deal Analysis" navigation section and solidifies their roles, guiding both users and future development.

## Workflow 1: The Deal Verdict Wizard

- **Purpose**: A simplified, 5-step guided process for investors who need a rapid, cash-flow-based verdict on a property. It focuses on the most critical inputs to answer the question: "Is this a good passive rental?"
- **Audience**: Passive investors, users new to real estate underwriting, or users who need to quickly screen many deals.
- **Implementation**: This workflow is already implemented and self-contained within `src/deal_verdict_wizard.py`. It will remain the primary, quick-start option.

## Workflow 2: The Deep Dive Analysis

- **Purpose**: A comprehensive, multi-step analysis covering all aspects of an investment, from market fundamentals and value-add modeling to long-term projections and advanced tax strategies.
- **Audience**: Sophisticated investors, professional underwriters, or users who have passed the initial verdict and want to perform detailed due diligence.
- **Implementation**: This workflow is composed of the other pages in the "Deal Analysis" section, which function as guided "mini-wizards" for each stage of the analysis. The intended sequence is:
  1.  **Market & Property Fundamentals** (`market_regulatory_intake.py`)
  2.  **Acquisition & Value-Add Modeling** (`acquisition_rehab_modeler.py`)
  3.  **Capital Markets & Leverage Simulator** (`capital_markets_simulator.py`)
  4.  **The Institutional Underwriting Engine** (`underwriting_engine.py`)
  5.  **Long-Term Proforma Generator** (`proforma_generator.py`)
  6.  **Tax Benefit Optimizer** (`tax_optimizer.py`)
  7.  **'Profit First' Cash Management** (`profit_first_allocator.py`)

## Relationship & Data Flow

- **Parallel, Not Sequential**: The two workflows are parallel paths to analyzing a deal, not a single, combined workflow. A user can choose which path is appropriate for their needs.
- **Shared State**: Both workflows operate on the same `deal_profile` object in `st.session_state`. This is a key feature, allowing a user to start with the quick wizard, then switch to a specific "Deep Dive" page to refine one part of the analysis (e.g., model a cost segregation study in the Tax Optimizer), and see the results reflected everywhere.
- **Complementary Detail**: The "Deep Dive" pages offer more detail and advanced modeling (e.g., BRRRR simulation, Cost Segregation, Proforma projections) that are out of scope for the streamlined Deal Verdict Wizard.

## Implementation Plan

- **Documentation**: This plan document serves as the primary artifact to formalize the architectural intent.
- **UI Guidance**: The existing structure, where each "Deep Dive" page provides a "Next, proceed to..." prompt, effectively guides the user through the workflow. This will be maintained and reinforced.
- **Finalize Workflow Prompt**: Add a concluding prompt to the final step of the Deep Dive workflow (`profit_first_allocator.py`) to guide the user to the `Deal Summary Report`, signaling the completion of the analysis.

This dual-workflow approach provides both a simple on-ramp for new users and the depth required by expert users, all while maintaining a consistent underlying data model.
