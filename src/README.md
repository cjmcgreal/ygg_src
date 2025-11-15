# Personal Dashboard - Streamlit Application

A modular Streamlit application organized by domain-specific subapps.

## Quick Start

```bash
streamlit run app.py
```

## Project Structure

```
src/
├── app.py                      # Main aggregator - brings all domains together
├── app_cfg.py                  # Central configuration for all domains
├── domains/                    # Domain-specific subapps
│   ├── exercise/              # Exercise tracking domain
│   │   ├── exercise_app.py           # UI component (render_exercise_app)
│   │   ├── exercise_workflow.py      # API/workflow orchestration
│   │   ├── exercise_logic.py         # Business logic
│   │   ├── exercise_analysis.py      # Data analysis functions
│   │   ├── exercise_db.py            # CSV database interface
│   │   └── exercise_data/            # CSV data files
│   │       └── exercises.csv
│   ├── finance/               # Finance tracking domain (template)
│   │   ├── finance_app.py
│   │   └── finance_data/
│   ├── task_management/       # Task management domain (template)
│   │   ├── task_management_app.py
│   │   └── task_management_data/
│   ├── travel/                # Travel planning domain (template)
│   │   ├── travel_app.py
│   │   └── travel_data/
│   └── trees/                 # Trees visualization domain (template)
│       ├── trees_app.py
│       └── trees_data/
└── README.md                   # This file
```

## Architecture

### Navigation Pattern
- **Sidebar**: Navigate between different domains (Trees, Exercise, Finance, etc.)
- **Domain Tabs**: Each domain can have its own tabs for organizing sub-sections
- **Example**: Exercise domain has tabs for Overview, Exercise Data, and Analytics

### Main App (app.py)
- **Purpose**: Aggregates all domain subapps into a single Streamlit application
- **Pattern**: Sidebar radio buttons for domain selection, calls `render_{domain}_app()` for selected domain
- **Clean separation**: No business logic, just orchestration

### Domain Structure
Each domain follows a consistent 5-file pattern:

1. **`{domain}_app.py`** - Streamlit UI component
   - Contains `render_{domain}_app()` function
   - Handles user interactions
   - Calls workflow functions

2. **`{domain}_workflow.py`** - API interface layer
   - One function per user action
   - Orchestrates calls to logic, analysis, and db modules
   - Acts as controller between UI and backend

3. **`{domain}_logic.py`** - Business logic
   - Custom business rules
   - Validation functions
   - Pure functions when possible

4. **`{domain}_analysis.py`** - Data analysis
   - Data processing and calculations
   - Statistical operations
   - Uses pandas for data manipulation

5. **`{domain}_db.py`** - CSV database interface
   - CRUD operations for CSV files
   - Abstracts file I/O from other layers

### Data Organization
- Each domain stores CSV files in `{domain}_data/` folder
- CSVs act as mock databases for prototyping
- Configured in `app_cfg.py`

## Current Domains

### 1. Exercise (Fully Implemented Example)
- **Status**: ✓ Complete template with all 5 files
- **Features**: Track exercises with reps, display summary statistics
- **Domain Tabs**: Overview, Exercise Data, Analytics (demonstrates in-domain tab navigation)
- **Data**: `domains/exercise/exercise_data/exercises.csv`

### 2. Finance (Template)
- **Status**: ○ Basic template only
- **To Implement**: Add workflow, logic, analysis, and db modules

### 3. Task Management (Template)
- **Status**: ○ Basic template only
- **To Implement**: Add workflow, logic, analysis, and db modules

### 4. Travel (Template)
- **Status**: ○ Basic template only
- **To Implement**: Add workflow, logic, analysis, and db modules

### 5. Trees (Template)
- **Status**: ○ Basic template only
- **To Implement**: Add workflow, logic, analysis, and db modules

## Adding a New Domain

1. **Create domain folder structure**:
   ```bash
   mkdir -p domains/new_domain/new_domain_data
   ```

2. **Create the 5 required files**:
   - `new_domain_app.py` with `render_new_domain_app()` function
   - `new_domain_workflow.py`
   - `new_domain_logic.py`
   - `new_domain_analysis.py`
   - `new_domain_db.py`

3. **Add configuration to `app_cfg.py`**:
   ```python
   NEW_DOMAIN_DATA_DIR = "domains/new_domain/new_domain_data"
   NEW_DOMAIN_CSV_PATH = f"{NEW_DOMAIN_DATA_DIR}/data.csv"
   ```

4. **Update `app.py`** to import and render the new domain:
   ```python
   from domains.new_domain.new_domain_app import render_new_domain_app

   # Add to tabs
   tab_new = st.tabs(["...", "New Domain"])

   with tab_new:
       render_new_domain_app()
   ```

5. **Create sample CSV data** in `domains/new_domain/new_domain_data/`

## Code Style

- **Readability first**: Code should be clear and easy to understand
- **Comments**: Explain WHY, not just WHAT
- **Docstrings**: Every function should have purpose, parameters, and return value documented
- **Standalone tests**: Each file includes `if __name__ == "__main__":` section for manual testing
- **Naming conventions**:
  - Files: `{domain}_module.py`
  - Functions: `render_{domain}_app()`, `get_data()`, etc.
  - DataFrames: Suffix with `_df` (e.g., `users_df`)

## Testing

Run individual modules standalone:
```bash
python domains/exercise/exercise_logic.py
python domains/exercise/exercise_analysis.py
python domains/exercise/exercise_db.py
```

View configuration:
```bash
python app_cfg.py
```

## Dependencies

```
streamlit
pandas
pytest
```

Install with:
```bash
pip install streamlit pandas pytest
```

## Notes

- The Exercise domain is fully implemented as a reference example
- Other domains (finance, task_management, travel, trees) are templates ready for implementation
- Each domain is independent and can be developed separately
- The modular structure makes it easy to add, remove, or modify domains without affecting others
