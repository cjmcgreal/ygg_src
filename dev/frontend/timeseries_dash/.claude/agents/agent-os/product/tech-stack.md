# Tech Stack

## Framework & Runtime
- **Application Framework:** Plotly Dash (v3 implementation) / Streamlit (v2 implementation)
- **Language/Runtime:** Python 3.8+
- **Package Manager:** pip

## Frontend
- **JavaScript Framework:** Dash React components / Streamlit's built-in components
- **CSS Framework:** Bootstrap 5 (via dash-bootstrap-components / Streamlit)
- **UI Components:**
  - Dash Bootstrap Components (dbc) for v3
  - Streamlit native components for v2
  - Font Awesome icons for visual indicators
- **Charting Library:** Plotly.js (via plotly.py)
- **Interactive Features:** Native HTML5 drag-and-drop API with custom JavaScript callbacks

## Data Layer
- **Data Format:** CSV files (no database required)
- **Data Processing:** Pandas DataFrames for all data manipulation
- **Data Files:**
  - `timeseries_data.csv` - Main timeseries data with timestamp column
  - `channel_tags.csv` - Channel metadata and hierarchy definitions
- **Timestamp Handling:** Pandas datetime objects with timezone support

## Analysis & Computation
- **Data Analysis:** Pandas for aggregation, filtering, and transformations
- **Numerical Operations:** NumPy for efficient array operations
- **Time Aggregation:** Pandas `resample()` and `groupby()` methods
- **Aggregation Methods:** Built-in pandas functions (mean, sum, min, max, median)

## Project Structure
- **Architecture Pattern:** Domain-based layered architecture
- **Code Organization:**
  - `app.py` - Main application entry point
  - `src/timeseries/` - Timeseries domain module
    - `timeseries_db.py` - Data loading layer (CSV I/O)
    - `timeseries_analysis.py` - Data aggregation and processing
    - `timeseries_workflow.py` - Orchestration layer (v2)
    - `timeseries_logic.py` - Business rules (v2)
    - `timeseries_app.py` - UI components (v2 Streamlit)
    - `timeseries_data/` - CSV data files
  - `tests/` - Test suite mirroring src structure

## Testing & Quality
- **Test Framework:** pytest
- **Test Structure:** Domain-based test organization matching src structure
- **Test Types:**
  - Unit tests for individual functions
  - Standalone test sections (`if __name__ == "__main__"`) in each module
- **Code Quality:** Self-documenting code with minimal comments

## Development Workflow
- **Local Development:** Run directly with `python app.py` or `streamlit run app.py`
- **Hot Reload:**
  - Dash debug mode for v3
  - Streamlit auto-reload for v2
- **Port Configuration:** Default port 8050 (Dash) or 8501 (Streamlit)

## Dependencies
**Core Framework (v3 - Dash):**
- `dash>=2.14.0`
- `dash-bootstrap-components>=1.5.0`
- `dash-extensions>=1.0.0`

**Core Framework (v2 - Streamlit):**
- `streamlit>=1.28.0`

**Shared Dependencies:**
- `plotly>=5.17.0` - Interactive charting
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical operations
- `pytest>=7.4.0` - Testing framework

## Deployment & Infrastructure
- **Hosting:** Local development / Any Python-capable web server
- **Infrastructure Requirements:** None - runs as standalone Python web app
- **Data Storage:** Local filesystem (CSV files)
- **Scalability:** Designed for datasets up to ~100K data points per channel

## Third-Party Services
- **Authentication:** Not implemented (prototype/internal tool)
- **Monitoring:** Not implemented
- **Analytics:** Not implemented

## Browser Requirements
- **Minimum Browser Version:** Modern browsers with HTML5 drag-and-drop support
- **Recommended:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript:** Required for drag-and-drop and Plotly interactivity
- **Responsive Support:** Desktop and laptop screens (1280px+ recommended)
