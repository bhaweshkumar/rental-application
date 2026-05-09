# Comprehensive Software Requirement Specification (SRS)

## Passive Real Estate Underwriting & Evaluation Engine

### 1. Executive Summary

This specification outlines a locally hosted, institutional-grade Python application (built with Streamlit) designed to evaluate rental property investments. The system adheres to a passive, "day-job investor" mandate by removing emotional bias, strictly evaluating the mathematics of a deal using the "Big Four" metrics, and benchmarking properties against 2026 macroeconomic standards, regulatory environments, and advanced financing structures (DSCR, BRRRR).

### 2. Technology Stack

- **Frontend / UI:** Streamlit (Python) for rapid, responsive dashboard development.
- **Backend Logic:** Python utilizing Pandas and NumPy for multi-year proformas, DCF (Discounted Cash Flow) calculations, and financial modeling.
- **Database:** Local SQLite or JSON document storage to save, compare, and retrieve "Deal Profiles".
- **External Integrations:** Webhook listener (FastAPI or Streamlit native) to receive automated lead data from Make.com/Zapier. The system will use a multi-source data strategy for property data, ARV, and rent estimates, detailed in Feature 9.

---

### 3. Feature Breakdown

This application is broken down into the following core features. Each feature is detailed in its own specification document.

- Feature 1: Market & Regulatory Intake
- Feature 2: Acquisition & Rehab Modeler
- Feature 3: Capital Markets & Leverage Simulator
- Feature 4: The Institutional Underwriting Engine
- Feature 5: 3-Year Proforma & DCF Generator
- Feature 6: BRRRR Refinance & Tax Optimization Modeler
- Feature 7: "Profit First" Cash Allocation Blueprint
- Feature 8: Automated Lead Funnel Integrator (CRM)
- Feature 9: Multi-Source Data Integration Strategy

---

### 4. Implementation Phasing Strategy

- **Phase 1 (Core Evaluator):** Build Features 2, 3, and 4.
- **Phase 2 (Proforma & Strategy):** Build Features 1, 5, and 6.
- **Phase 3 (Operational Reality & Data Integration):** Build Features 7 and 9.
- **Phase 4 (Automation):** Build Feature 8.
