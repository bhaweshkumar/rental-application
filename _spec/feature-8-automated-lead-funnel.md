# Feature 8: Automated Lead Funnel Integrator (CRM)

## 1. Objective

Allow the app to act as a localized CRM that accepts JSON payloads from Zapier/Make.com webhooks triggered by conversational AI agents.

## 2. Detailed Specifications

### 2.1. UI Components

- A "Deal Pipeline" Kanban board or list view (Inbox, Underwriting, Offered, Rejected).

### 2.2. Backend Logic

- A Streamlit API endpoint or separate background process that listens for incoming JSON (Name, Phone, Property Address, Estimated Equity, Motivation Level).
- Automatically parses the payload and creates a new Deal Profile in the SQLite database.
- _Auto-Enrichment Trigger:_ Upon receiving a new lead, the system will automatically query the configured data sources (see Feature 9) to fetch property characteristics, tax history, and estimated rent/ARV, pre-populating the deal profile for rapid underwriting.

### 2.3. Outputs

- A notification in the UI indicating "New AI Lead Received," with the property automatically scored based on the Big Four metrics.

## 3. Acceptance Criteria

**Scenario 1: Receiving and processing a new lead via webhook.**

- **Given** the application's webhook listener is active.
- **When** a POST request is sent to the webhook endpoint with a valid JSON payload.
- **Then** the backend should parse the JSON and create a new "Deal Profile" in the local database.
- **And** the new deal should appear in the "Inbox" column of the "Deal Pipeline" UI.
- **And** a notification "New AI Lead Received" should be displayed.

**Scenario 2: Auto-enrichment of a new lead.**

- **Given** a new lead has been created via webhook.
- **And** the data integration module (Feature 9) is configured with a valid API key.
- **When** the new lead is processed.
- **Then** the system must automatically trigger an API call to the configured data source.
- **And** it should attempt to fetch property data (sqft, bed/bath), tax history, and estimated rent/ARV.
- **And** the fetched data should be used to pre-populate the corresponding fields in the new Deal Profile.
- **And** the system should attempt to run an initial underwriting score based on the enriched data.
