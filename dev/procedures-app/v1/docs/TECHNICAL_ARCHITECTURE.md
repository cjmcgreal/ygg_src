# Technical Architecture

## Overview

The Procedures Management App is built as a Python Streamlit application with CSV-based data storage, optimized for rapid iteration and transparent data management.

## Architecture Principles

1. **Simplicity First**: Choose the simplest solution that works
2. **Data Transparency**: Users can inspect and modify data files directly
3. **Git-Friendly**: All data in text-based formats for version control
4. **Clear Separation**: Distinct layers for UI, workflows, logic, and data
5. **Easy Migration Path**: Architecture supports future database migration

---

## Technology Stack

### Core Technologies

**Frontend/UI**
- **Streamlit** (Python web framework)
  - Rapid prototyping and iteration
  - Built-in state management
  - Automatic reactivity
  - Mobile-responsive by default
  - No separate frontend build process required

**Data Storage**
- **CSV files** (human-readable, git-friendly)
  - `procedures.csv`: Procedure definitions
  - `steps.csv`: Individual steps for each procedure
  - `runs.csv`: Execution history
  - `run_steps.csv`: Step-level execution details
  - `labels.csv`: Label definitions
  - `procedure_labels.csv`: Many-to-many mapping
  - `versions.csv`: Procedure version history

**Data Manipulation**
- **Pandas** (Python data analysis library)
  - DataFrame operations for CRUD
  - Fast filtering and aggregation
  - Built-in CSV read/write
  - Analytics and reporting

**Development Tools**
- **Python 3.9+**
- **Virtual environment** (venv or conda)
- **Git** for version control
- **pytest** for testing
- **Black** for code formatting
- **Flake8** for linting

---

## Project Structure

```
procedures-app/
│
├── app.py                  # Main Streamlit application entry point
├── requirements.txt        # Python dependencies
├── README.md              # Setup and usage instructions
│
├── src/
│   ├── __init__.py
│   ├── workflow.py        # UI workflows and page interactions
│   ├── logic.py           # Business logic and rules
│   ├── database.py        # CSV read/write operations
│   ├── analysis.py        # Analytics and metrics calculations
│   └── utils.py           # Helper functions and utilities
│
├── data/                  # CSV data storage
│   ├── procedures.csv
│   ├── steps.csv
│   ├── runs.csv
│   ├── run_steps.csv
│   ├── labels.csv
│   ├── procedure_labels.csv
│   └── versions.csv
│
├── tests/                 # Unit and integration tests
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_logic.py
│   ├── test_analysis.py
│   └── fixtures/          # Test CSV fixtures
│
└── docs/                  # Documentation
    ├── PRODUCT_MISSION.md
    ├── PRODUCT_ROADMAP.md
    ├── TARGET_AUDIENCE.md
    ├── FEATURES_AND_DIFFERENTIATORS.md
    ├── SUCCESS_METRICS.md
    └── TECHNICAL_ARCHITECTURE.md (this file)
```

---

## Module Responsibilities

### `app.py` - Application Entry Point

**Responsibilities**:
- Initialize Streamlit app
- Configure page settings (title, layout, theme)
- Handle routing between different pages/views
- Manage global state
- Render main navigation

**Example Structure**:
```python
import streamlit as st
from src.workflow import render_browser, render_execution, render_history

st.set_page_config(page_title="Procedures App", layout="wide")

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", ["Browser", "Execute", "History", "Analytics"])

if page == "Browser":
    render_browser()
elif page == "Execute":
    render_execution()
elif page == "History":
    render_history()
```

---

### `src/workflow.py` - UI Workflows

**Responsibilities**:
- Define page layouts and components
- Handle user interactions (button clicks, form submissions)
- Manage page-specific state
- Call business logic functions
- Display results to user

**Key Functions**:
- `render_browser()`: Procedure list view
- `render_execution()`: Step-by-step execution interface
- `render_history()`: Run log and filtering
- `render_analytics()`: Metrics dashboard
- `render_editor()`: Procedure creation/editing form

**Example**:
```python
def render_browser():
    st.title("Procedures")

    # Search and filter
    search = st.text_input("Search procedures")
    label_filter = st.multiselect("Filter by label", get_all_labels())

    # Get filtered procedures
    procedures = logic.get_procedures(search=search, labels=label_filter)

    # Display procedures
    for proc in procedures:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"**{proc['name']}**")
        col2.write(f"{proc['step_count']} steps")
        if col3.button("Start", key=proc['id']):
            st.session_state.active_procedure = proc['id']
            st.rerun()
```

---

### `src/logic.py` - Business Logic

**Responsibilities**:
- Implement core business rules
- Orchestrate data operations
- Validate user inputs
- Calculate derived values
- Manage procedure execution state

**Key Functions**:
- `create_procedure(name, description, steps)`: Create new procedure
- `start_run(procedure_id)`: Initialize procedure execution
- `complete_step(run_id, step_id)`: Mark step as done
- `finish_run(run_id, status)`: Complete or cancel a run
- `calculate_completion_rate(procedure_id)`: Analytics calculation
- `get_version_history(procedure_id)`: Retrieve version log

**Example**:
```python
def start_run(procedure_id: int) -> int:
    """Initialize a new procedure run"""
    # Validate procedure exists
    procedure = database.get_procedure_by_id(procedure_id)
    if not procedure:
        raise ValueError(f"Procedure {procedure_id} not found")

    # Create run record
    run_id = database.create_run({
        'procedure_id': procedure_id,
        'start_time': datetime.now(),
        'status': 'in_progress'
    })

    # Initialize step tracking
    steps = database.get_steps_for_procedure(procedure_id)
    for step in steps:
        database.create_run_step({
            'run_id': run_id,
            'step_id': step['id'],
            'completed': False
        })

    return run_id
```

---

### `src/database.py` - Data Layer

**Responsibilities**:
- Read and write CSV files
- Provide CRUD operations
- Handle data validation
- Manage data integrity (foreign keys, constraints)
- Implement atomic writes to prevent corruption

**Key Functions**:
- `load_table(table_name)`: Load CSV into DataFrame
- `save_table(table_name, df)`: Write DataFrame to CSV
- `get_procedure_by_id(id)`: Retrieve single procedure
- `create_procedure(data)`: Insert new procedure
- `update_procedure(id, data)`: Modify existing procedure
- `delete_procedure(id)`: Remove procedure (cascade to steps)

**Example**:
```python
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

def load_table(table_name: str) -> pd.DataFrame:
    """Load CSV table into DataFrame"""
    file_path = DATA_DIR / f"{table_name}.csv"
    if not file_path.exists():
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=get_schema(table_name))
    return pd.read_csv(file_path)

def save_table(table_name: str, df: pd.DataFrame):
    """Save DataFrame to CSV"""
    file_path = DATA_DIR / f"{table_name}.csv"
    df.to_csv(file_path, index=False)

def get_procedure_by_id(procedure_id: int) -> dict:
    """Retrieve single procedure by ID"""
    df = load_table("procedures")
    result = df[df['id'] == procedure_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()
```

---

### `src/analysis.py` - Analytics

**Responsibilities**:
- Calculate metrics and KPIs
- Generate reports
- Perform statistical analysis
- Create data for visualizations

**Key Functions**:
- `get_completion_rate(procedure_id)`: % of runs completed
- `get_average_duration(procedure_id)`: Mean execution time
- `get_run_frequency(procedure_id, period)`: Runs per week/month
- `get_bottleneck_steps(procedure_id)`: Slowest steps
- `get_procedure_trends(procedure_id)`: Time series data

**Example**:
```python
def get_completion_rate(procedure_id: int) -> float:
    """Calculate completion rate for a procedure"""
    runs_df = database.load_table("runs")
    proc_runs = runs_df[runs_df['procedure_id'] == procedure_id]

    if len(proc_runs) == 0:
        return 0.0

    completed = len(proc_runs[proc_runs['status'] == 'completed'])
    total = len(proc_runs)

    return (completed / total) * 100
```

---

### `src/utils.py` - Helper Functions

**Responsibilities**:
- Common utility functions
- Date/time formatting
- ID generation
- Validation helpers

**Key Functions**:
- `generate_id()`: Create unique IDs
- `format_duration(seconds)`: Human-readable time
- `validate_procedure_data(data)`: Input validation
- `safe_divide(a, b)`: Avoid division by zero in analytics

---

## Data Schema

### `procedures.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier (auto-increment) |
| name | str | Procedure name |
| description | str | Optional description |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last modification timestamp |
| version | int | Current version number |

### `steps.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| procedure_id | int | Foreign key to procedures |
| order | int | Step sequence (1, 2, 3...) |
| description | str | Step instruction text |
| estimated_duration | int | Optional: seconds |

### `runs.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| procedure_id | int | Foreign key to procedures |
| start_time | datetime | When run started |
| end_time | datetime | When run finished (nullable) |
| status | str | 'in_progress', 'completed', 'cancelled' |
| notes | str | Optional user notes |

### `run_steps.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| run_id | int | Foreign key to runs |
| step_id | int | Foreign key to steps |
| completed | bool | Step completion status |
| completed_at | datetime | When step was marked done |
| notes | str | Optional step-specific notes |

### `labels.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| name | str | Label name (e.g., "weekly") |
| color | str | Hex color code for UI |

### `procedure_labels.csv`

| Column | Type | Description |
|--------|------|-------------|
| procedure_id | int | Foreign key to procedures |
| label_id | int | Foreign key to labels |

### `versions.csv`

| Column | Type | Description |
|--------|------|-------------|
| id | int | Unique identifier |
| procedure_id | int | Foreign key to procedures |
| version | int | Version number |
| created_at | datetime | When version was created |
| change_description | str | What changed |
| procedure_snapshot | json | Full procedure state as JSON |

---

## State Management

### Streamlit Session State

Store transient UI state in `st.session_state`:

```python
# Active procedure being executed
st.session_state.active_procedure_id = None
st.session_state.active_run_id = None

# Current page/view
st.session_state.current_page = "browser"

# Filter states
st.session_state.search_query = ""
st.session_state.selected_labels = []
```

### Data Persistence

All persistent data stored in CSV files:
- Automatically loaded on page render
- Written immediately after mutations
- Atomic writes to prevent corruption

---

## Performance Considerations

### CSV File Size Limits

**Expected Scale (Year 1)**:
- ~10,000 procedures
- ~100,000 steps
- ~500,000 runs
- CSV files: ~50-100 MB total

**Performance Strategy**:
- Pandas handles this efficiently
- If files exceed 1M rows: migrate to SQLite
- If multi-user: migrate to PostgreSQL

### Optimization Techniques

1. **Lazy Loading**: Only load tables when needed
2. **Caching**: Use `@st.cache_data` for expensive operations
3. **Indexing**: Keep ID columns first for faster lookups
4. **Filtering Early**: Apply filters before loading full DataFrames

---

## Testing Strategy

### Unit Tests

**Coverage Goals**: >80% code coverage

**Test Files**:
- `test_database.py`: CRUD operations, data integrity
- `test_logic.py`: Business rules, validation
- `test_analysis.py`: Metric calculations
- `test_utils.py`: Helper functions

**Example Test**:
```python
def test_start_run():
    """Test starting a new procedure run"""
    procedure_id = logic.create_procedure("Test Procedure", "Description", [
        "Step 1", "Step 2", "Step 3"
    ])

    run_id = logic.start_run(procedure_id)

    assert run_id is not None
    run = database.get_run_by_id(run_id)
    assert run['status'] == 'in_progress'
    assert run['procedure_id'] == procedure_id
```

### Integration Tests

- End-to-end workflows (create → execute → complete)
- CSV file integrity after operations
- State management across page transitions

### Manual Testing Checklist

- [ ] Create procedure with 10 steps
- [ ] Execute procedure, complete all steps
- [ ] Cancel procedure mid-execution
- [ ] Filter procedures by label
- [ ] View run history
- [ ] Edit procedure and verify version created
- [ ] Export data to CSV

---

## Deployment

### Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt

# Run app
streamlit run app.py
```

### Production Deployment Options

**Option 1: Streamlit Cloud** (Recommended for MVP)
- Free tier for public apps
- Deploy directly from GitHub
- Automatic HTTPS and scaling
- No server management required

**Option 2: Self-Hosted (Docker)**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

**Option 3: Cloud VM** (AWS, GCP, Azure)
- Deploy on EC2/Compute Engine
- Use systemd or supervisor for process management
- Nginx reverse proxy for HTTPS

---

## Data Backup Strategy

### Automated Backups

**Daily Backups**:
- Copy entire `data/` directory to `backups/YYYY-MM-DD/`
- Retain last 30 days
- Automate with cron job or GitHub Actions

**Git-Based Backups**:
- Commit CSV files to git repository
- Push to remote (GitHub/GitLab)
- Provides version history and rollback capability

### Recovery Procedures

1. Identify backup date to restore
2. Stop application
3. Replace `data/` directory with backup
4. Restart application
5. Verify data integrity

---

## Migration Path to Database

### When to Migrate

**Triggers**:
- CSV files exceed 1M rows
- Performance degrades (load times >2 seconds)
- Multi-user concurrency needed
- Advanced querying required

### Migration Strategy

**Phase 1: SQLite** (for single-user or small teams)
- Keep same data schema
- Update `database.py` to use SQLAlchemy
- Minimal code changes in other modules
- Support CSV export for backwards compatibility

**Phase 2: PostgreSQL** (for multi-tenant SaaS)
- Add user authentication
- Multi-tenancy (isolate data per organization)
- Advanced indexing and query optimization
- API layer for mobile apps

---

## Security Considerations

### Current (MVP)

- **Data Privacy**: All data stored locally, user controls access
- **Input Validation**: Sanitize user inputs to prevent injection
- **No Authentication**: Single-user app, no login required

### Future (Multi-User)

- **Authentication**: OAuth2 or JWT-based login
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: Encrypt sensitive data at rest
- **Audit Logging**: Track all data modifications
- **API Security**: Rate limiting, HTTPS-only

---

## Monitoring and Logging

### Application Logs

**Log Levels**:
- ERROR: Data corruption, crashes
- WARNING: Validation failures, edge cases
- INFO: User actions (procedure created, run started)
- DEBUG: Detailed execution flow (development only)

**Implementation**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Procedure execution started", extra={"procedure_id": 123})
```

### Error Tracking

- **Sentry** integration for production error monitoring
- Capture stack traces and user context
- Alert on critical errors

---

## Development Workflow

### Git Workflow

**Branches**:
- `main`: Production-ready code
- `develop`: Integration branch
- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes

**Commit Messages**:
- Use conventional commits format
- Examples: `feat: add version history`, `fix: execution pause bug`

### Code Review Process

1. Create feature branch
2. Implement changes with tests
3. Open pull request to `develop`
4. Automated tests run via GitHub Actions
5. Code review by team member
6. Merge after approval

### Release Process

1. Merge `develop` → `main`
2. Tag release (e.g., `v0.1.0`)
3. Deploy to production
4. Monitor for issues
5. Create release notes

---

## Dependencies

### Core Dependencies (`requirements.txt`)

```
streamlit==1.28.0
pandas==2.1.0
pytest==7.4.0
black==23.9.0
flake8==6.1.0
```

### Optional Dependencies

```
# Analytics and visualization
plotly==5.17.0
matplotlib==3.8.0

# Error tracking
sentry-sdk==1.32.0

# Testing
pytest-cov==4.1.0
```

---

## Future Technical Enhancements

### API Layer (REST or GraphQL)
- Enable third-party integrations
- Mobile app backend
- Webhook support for automation

### Real-Time Collaboration
- WebSocket support for live updates
- Shared procedure execution
- Team dashboards

### Advanced Analytics
- Machine learning for optimization suggestions
- Predictive completion times
- Anomaly detection

### Mobile Apps
- React Native or Flutter
- Offline-first architecture
- Camera integration for photo steps

---

## Conclusion

This architecture balances simplicity, transparency, and scalability. The CSV-based approach enables rapid iteration during MVP phase while maintaining a clear path to more robust infrastructure as the product grows.

**Key Strengths**:
- Fast to build and iterate
- No database setup required
- Git-friendly and user-inspectable
- Clear separation of concerns
- Easy to test

**Migration Triggers**:
- Performance degradation
- Multi-user requirements
- Advanced querying needs
- Regulatory/compliance requirements

The architecture is intentionally designed to be replaced incrementally—each module can be upgraded independently without rewriting the entire application.
