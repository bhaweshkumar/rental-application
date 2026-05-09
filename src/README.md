# Passive Real Estate Underwriting & Evaluation Engine

This is a locally hosted, institutional-grade Python application (built with Streamlit) designed to evaluate rental property investments. The system adheres to a passive, "day-job investor" mandate by removing emotional bias, strictly evaluating the mathematics of a deal using the "Big Four" metrics, and benchmarking properties against 2026 macroeconomic standards.

## Overview

This project is based on the "The Scalable and Passive Rental Property Playbook" and aims to provide a comprehensive tool for real estate investors.

## Tech Stack

- **Frontend / UI:** Streamlit
- **Backend Logic:** Python, Pandas, NumPy
- **Database:** Local SQLite / JSON

## Setup and Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd rental-application
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    streamlit run src/app.py
    ```
