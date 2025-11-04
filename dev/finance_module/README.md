# Finance Dashboard

A sophisticated finance tracking and analysis dashboard built with Plotly Dash, pandas, and Python.

## Features

### ✨ Core Functionality
- **CSV Import**: Import bank/credit card transaction data from CSV files
- **Hierarchical Categories**: Nested category system (e.g., `transportation/car/gas`)
- **Auto-Labeling**: Substring-based automatic transaction categorization
- **Approval Workflow**: Lock approved labels to prevent overwrites
- **Interactive Visualizations**: Time series, category breakdowns, and more

### 📊 Dashboard Tabs

1. **Overview**: High-level metrics and visualizations
   - Total income, expenses, and net
   - Spending over time (time series)
   - Category breakdown (pie chart)

2. **Import Data**: CSV upload and import workflow
   - Upload CSV files
   - Auto-labeling option
   - Import statistics

3. **Manage Categories**: Category and rule management
   - View category hierarchy
   - Add new categories
   - Create substring matching rules

4. **Review Transactions**: Transaction review and approval
   - Filter transactions by date, category, amount, text
   - Approve/edit transaction labels
   - Batch operations

## Installation

### Requirements
- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: From project root
```bash
cd finance_module
python src/finance/finance_app.py
```

### Method 2: From finance directory
```bash
cd finance_module/src/finance
python finance_app.py
```

The application will start on `http://127.0.0.1:8050/`

## Project Structure

```
finance_module/
├── src/finance/
│   ├── finance_app.py          # Main Dash application
│   ├── finance_workflow.py     # Workflow orchestration
│   ├── finance_analysis.py     # Data analysis functions
│   ├── finance_logic.py        # Business logic
│   ├── finance_db.py           # Database (CSV) operations
│   └── finance_data/           # CSV data files
│       ├── transactions.csv
│       ├── categories.csv
│       ├── label_rules.csv
│       └── transaction_approvals.csv
├── tests/finance/              # Unit and integration tests
│   ├── test_finance_db.py
│   ├── test_finance_logic.py
│   ├── test_finance_analysis.py
│   └── test_finance_workflow.py
└── requirements.txt            # Python dependencies
```

## Architecture

The application follows a layered architecture:

1. **UI Layer** (`finance_app.py`): Plotly Dash interface with tabs
2. **Workflow Layer** (`finance_workflow.py`): Orchestrates user actions
3. **Analysis Layer** (`finance_analysis.py`): Time grouping, rollups, statistics
4. **Logic Layer** (`finance_logic.py`): Business rules, validation, matching
5. **Database Layer** (`finance_db.py`): CSV file operations (CRUD)

## Data Format

### CSV Import Format
Your CSV file should have these columns:

```csv
date,description,amount,account
2025-01-15,STARBUCKS COFFEE,-5.50,Chase Credit
2025-01-16,UBER RIDE,-45.00,Chase Credit
2025-01-19,PAYCHECK DEPOSIT,3500.00,Chase Checking
```

**Required columns:**
- `date`: Transaction date (YYYY-MM-DD)
- `description`: Transaction description
- `amount`: Amount (negative for expenses, positive for income)

**Optional columns:**
- `account`: Account name
- `original_category`: Category from bank (optional)

## Usage Guide

### 1. Import Transactions

1. Go to "Import Data" tab
2. Click "Select CSV File" and choose your transaction CSV
3. Check "Auto-label transactions" if you want automatic categorization
4. Click "Import Transactions"

### 2. Setup Categories

1. Go to "Manage Categories" tab
2. Add categories using the hierarchy format:
   - Root: `transportation`
   - Level 1: `transportation/car`
   - Level 2: `transportation/car/gas`

### 3. Create Label Rules

1. In "Manage Categories" tab, scroll to "Label Rules"
2. Add substring matching rules:
   - Substring: `starbucks`
   - Category: `dining/coffee`
   - Priority: `10` (higher = checked first)

### 4. Review and Approve

1. Go to "Review Transactions" tab
2. Apply filters to find specific transactions
3. Review auto-assigned labels
4. Approve correct labels to lock them

### 5. View Analytics

1. Go to "Overview" tab
2. Select date range
3. View metrics and charts
4. Charts update based on selected date range

## Key Features Explained

### Hierarchical Categories

Categories can be nested indefinitely:
```
transportation
├── car
│   ├── gas
│   ├── maintenance
│   └── insurance
└── air_travel
```

When viewing spending for `transportation`, it automatically includes all subcategories.

### Auto-Labeling

Define substring patterns to automatically categorize:
- "starbucks" → `dining/coffee`
- "uber" → `transportation/rideshare`
- "shell" → `transportation/car/gas`

Rules are checked in priority order (highest first).

### Approval Workflow

Once you approve a transaction's category:
1. The label is locked
2. Future auto-labeling won't overwrite it
3. Re-importing the same transaction preserves the approved label

## Testing

Run the test suite:

```bash
# All tests
pytest tests/finance/ -v

# Specific test file
pytest tests/finance/test_finance_workflow.py -v

# With coverage
pytest tests/finance/ --cov=src/finance --cov-report=html
```

**Test Results:**
- Database layer: 18 tests
- Business logic: 19 tests
- Analysis layer: 19 tests
- Workflow layer: 16 tests
- **Total: 72 tests ✅**

## Sample Data

Sample data files are included in `src/finance/finance_data/`:
- `sample_transactions.csv`: 20 realistic transactions
- `sample_categories.csv`: 27 hierarchical categories
- `sample_label_rules.csv`: 34 labeling rules
- `sample_approvals.csv`: 7 approved transactions

To use sample data:
```bash
# Copy sample files to active files
cd src/finance/finance_data
cp sample_transactions.csv transactions.csv
cp sample_categories.csv categories.csv
cp sample_label_rules.csv label_rules.csv
cp sample_approvals.csv transaction_approvals.csv
```

## Development

### Code Style
- Follow Python prototype development standards
- Comprehensive docstrings for all functions
- Type hints where beneficial
- Standalone test sections in each module

### Running Individual Modules

Each module can be run standalone:

```bash
cd src/finance
python finance_db.py           # Test database operations
python finance_logic.py        # Test business logic
python finance_analysis.py     # Test analysis functions
python finance_workflow.py     # Test workflows
```

## Future Enhancements

- [ ] Budget tracking and alerts
- [ ] Recurring transaction detection
- [ ] Machine learning for better auto-labeling
- [ ] Multi-user support
- [ ] Export reports (PDF, Excel)
- [ ] Mobile responsive design
- [ ] Real-time bank API integration

## License

MIT License

## Contributing

Contributions welcome! Please:
1. Write tests for new features
2. Follow existing code style
3. Update documentation
4. Run full test suite before submitting

## Support

For issues or questions, please open an issue on GitHub.
