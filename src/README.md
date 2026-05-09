# Passive Real Estate Underwriting & Evaluation Engine

This is a locally hosted, institutional-grade Python application (built with Streamlit) designed to evaluate rental property investments. The system adheres to a passive, "day-job investor" mandate by removing emotional bias, strictly evaluating the mathematics of a deal using the "Big Four" metrics, and benchmarking properties against 2026 macroeconomic standards.

## Overview

This project is based on the "The Scalable and Passive Rental Property Playbook" and aims to provide a comprehensive tool for real estate investors.

## Tech Stack

- **Frontend / UI:** Streamlit
- **Backend Logic:** Python, Pandas, NumPy
- **Database:** Local SQLite / JSON

## Running Under a Virtual Environment

Run the app from the repository root:

```bash
cd /path/to/rental-application
```

### 1. Create a virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 3. Install dependencies

Upgrade `pip` first, then install the app requirements:

```bash
python -m pip install --upgrade pip
python -m pip install -r src/requirements.txt
```

If you want to run the test suite locally, also install:

```bash
python -m pip install pytest requests
```

### 4. Start the Streamlit app

From the repository root:

```bash
streamlit run src/app.py
```

Then open the local URL printed by Streamlit, typically:

```text
http://localhost:8501
```

### 5. Run tests

```bash
python -m pytest -q src/test
```

### 6. Deactivate the virtual environment

```bash
deactivate
```

## Troubleshooting

- If `streamlit` is not found, make sure the virtual environment is activated.
- If dependency installation fails, confirm you are using `src/requirements.txt`, not `requirements.txt` at the repo root.
- If you changed Python versions, remove `.venv` and recreate it.

## Notes

- The application entrypoint is [app.py](/Users/bhaweshkumar/Projects/internal/rental-application/src/app.py).
- The Python dependency file currently used by the project is [requirements.txt](/Users/bhaweshkumar/Projects/internal/rental-application/src/requirements.txt).
