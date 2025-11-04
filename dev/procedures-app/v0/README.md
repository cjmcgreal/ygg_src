# Procedures Management App

A personal procedures management system for creating, executing, and refining repeatable task lists. Built with Python, Streamlit, and CSV-based storage for transparency and simplicity.

## Features

- **Procedure Browser**: View, search, and filter all your procedures
- **Step-by-Step Execution**: Guided interface for following procedures
- **Run History**: Complete audit trail of all executions
- **Analytics Dashboard**: Insights into completion rates, duration trends, and performance
- **Simple CSV Storage**: All data stored in human-readable CSV files

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

```bash
cd procedures-app
```

2. **Create a virtual environment** (recommended)

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

## Usage Guide

### 1. Creating a Procedure

1. Click "Create New Procedure" from the Browser page
2. Enter a name and optional description
3. Add steps (at least one required)
4. Use the "Add Step" button to add more steps
5. Click "Save" to create the procedure

**Example**: Create a "Clean Kitchen" procedure with steps like:
- Throw away all garbage
- Move dirty dishes to sink
- Load dishwasher
- etc.

### 2. Executing a Procedure

1. From the Browser, click "Start" on any procedure
2. Follow the steps one by one
3. Check off each step as you complete it
4. Click "Complete Run" when finished (or "Cancel" if interrupted)

### 3. Viewing History

1. Navigate to the History page
2. Filter by procedure, status, or date range
3. Expand any run to see detailed step-by-step information

### 4. Analytics

1. Navigate to the Analytics page
2. View overall statistics
3. See which procedures are run most frequently
4. Analyze completion rates across procedures

## Project Structure

```
procedures-app/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
│
├── src/                   # Source code
│   ├── workflow.py        # UI rendering and page logic
│   ├── logic.py           # Business logic
│   ├── database.py        # CSV data operations
│   ├── analysis.py        # Analytics calculations
│   └── utils.py           # Helper functions
│
├── data/                  # CSV data storage (created at runtime)
│   ├── procedures.csv
│   ├── steps.csv
│   ├── runs.csv
│   └── ...
│
├── tests/                 # Unit tests
└── docs/                  # Product documentation
```

## Data Storage

All data is stored in CSV files in the `data/` directory:

- **procedures.csv**: Procedure definitions
- **steps.csv**: Individual steps for each procedure
- **runs.csv**: Execution history
- **run_steps.csv**: Step-level execution tracking
- **labels.csv**: Label definitions (future feature)
- **procedure_labels.csv**: Label assignments (future feature)

You can inspect, backup, or modify these files directly with any spreadsheet application.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/ tests/
```

### Linting

```bash
flake8 src/ tests/
```

## Roadmap

See `docs/PRODUCT_ROADMAP.md` for the complete development plan.

**Phase 1 (MVP)** - ✅ Current
- Core procedure creation and execution
- Basic run history
- Simple CSV storage

**Phase 2** (Coming Soon)
- Enhanced analytics with charts
- Run notes and observations
- Date range filtering

**Phase 3**
- Version history for procedures
- Labels and organization
- Advanced editing features

## Troubleshooting

### App won't start

- Ensure you've activated the virtual environment
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.9+)

### Data not persisting

- Check that the `data/` directory exists
- Ensure you have write permissions in the app directory
- Look for error messages in the terminal

### Performance issues

- CSV files work well up to ~10,000 procedures and ~1M runs
- If you exceed these limits, consider the database migration path in `docs/TECHNICAL_ARCHITECTURE.md`

## Contributing

This is currently a personal project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [Pandas](https://pandas.pydata.org/) - Data manipulation
- [Plotly](https://plotly.com/) - Data visualization

---

**Made with ❤️ for productivity enthusiasts and process-oriented teams**
