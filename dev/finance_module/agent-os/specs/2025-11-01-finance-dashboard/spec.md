# Specification: Finance Dashboard

## Goal
Build a personal finance dashboard that imports bank/credit card transaction data from CSV files, automatically categorizes transactions using hierarchical labels with substring matching rules, and provides rich interactive visualizations for analyzing spending patterns over time.

## User Stories
- As a user, I want to import CSV files from my bank/credit card so that I can analyze my spending
- As a user, I want to define substring matching rules so that transactions are automatically categorized
- As a user, I want hierarchical categories (like "transportation/car/gas") so that I can analyze spending at different levels of detail
- As a user, I want to review and approve auto-assigned labels so that I maintain control over categorization
- As a user, I want approved labels to persist across re-imports so that my manual edits aren't lost
- As a user, I want interactive charts showing spending over time so that I can identify trends
- As a user, I want to see category rollups (parent category includes all subcategories) so that I understand total spending by major area
- As a user, I want to filter by date range and category so that I can drill into specific time periods or spending areas

## Core Requirements

### Functional Requirements

**1. Transaction Data Import**
- Upload CSV files containing transaction data (date, description, amount, optional account field)
- Parse and validate CSV structure
- Detect and handle duplicate transactions on re-import
- Store import history with timestamp
- Support multiple import sessions (append new data)

**2. Hierarchical Category System**
- Define unlimited nested categories using "/" delimiter (e.g., "housing/utilities/electric")
- Support arbitrary nesting depth (no hardcoded limit)
- Automatic parent-child relationship calculation
- Category display names and visualization colors
- Category CRUD operations through management interface

**3. Substring-Based Auto-Labeling**
- Define rules: substring + target category
- Case-insensitive substring matching by default
- Rule priority ordering (higher priority rules checked first)
- Enable/disable rules without deletion
- Apply rules automatically on import
- Show which rule was applied (for transparency)

**4. Transaction Label Approval Workflow**
- All imported transactions start as "pending approval"
- User can accept auto-assigned label (mark as approved)
- User can manually edit/change label and approve
- User can leave transaction unlabeled
- Approved labels are locked and persist across re-imports
- Review interface shows pending transactions sorted by amount or date
- Bulk approval actions (approve all with category X)

**5. Data Analysis & Aggregations**
- Time-based grouping: day, week, month, quarter, year
- Category rollup aggregations (parent includes all children)
- Total spending per period
- Total income per period
- Spending by category with hierarchical totals
- Period-over-period comparisons (this month vs last month)
- Moving averages for trend analysis
- Filter by date range, category, amount range, approval status

**6. Interactive Visualizations (Plotly Dash)**
- Time series line charts: spending/income over time with grouping selector
- Category breakdown pie charts: spending distribution
- Horizontal bar charts: top spending categories
- Stacked bar charts: category spending over time
- Treemap: hierarchical category visualization
- Comparison charts: period-over-period bars with growth indicators
- All charts interactive: zoom, pan, hover tooltips, click to drill down
- Date range picker for filtering
- Category filter dropdown with hierarchy display

**7. Dashboard Layout**
- Multi-tab interface with distinct sections:
  - **Overview**: Key metrics, primary time series, top categories
  - **Import Data**: Upload CSV, view import history, see new transactions
  - **Manage Categories**: Create/edit/delete categories, configure hierarchy
  - **Manage Rules**: Create/edit/delete substring matching rules, set priorities
  - **Review Transactions**: Approve/edit pending transaction labels, bulk actions
  - **Detailed Analysis**: Custom filters, advanced visualizations, export views

### Non-Functional Requirements

**Performance**
- Handle at least 10,000 transactions without noticeable lag
- Chart rendering should complete within 2 seconds
- CSV import should process within 5 seconds for files up to 5MB

**Data Integrity**
- Validate CSV structure before import
- Prevent duplicate transaction IDs
- Maintain referential integrity between transactions and approvals
- Automatic backup of CSV files before modifications

**Usability**
- Clear error messages for invalid CSV formats
- Visual indicators for approved vs pending transactions
- Intuitive category hierarchy display
- Responsive layout for different screen sizes
- Keyboard shortcuts for common actions (approve transaction, next transaction)

**Code Quality**
- Follow Python prototype development standards
- Clear separation: _app.py, _workflow.py, _logic.py, _analysis.py, _db.py
- Comprehensive docstrings explaining business logic
- Standalone test sections (if __name__ == "__main__") in each file
- Meaningful variable names with _df suffix for DataFrames

## Visual Design

No mockups provided. Use clean, modern Plotly Dash defaults with:
- Dark/light theme toggle
- Consistent color palette for categories
- Clear visual hierarchy (headings, spacing, grouping)
- Card-based layout for metrics
- Tab navigation for main sections
- Responsive grid layout

## Reusable Components

### Existing Code to Leverage

**From procedures-app project:**
- **CSV Database Pattern** (`database.py`):
  - `load_table()` and `save_table()` functions
  - Schema definition approach with `get_schema()`
  - Datetime column conversion logic
  - Directory path management with pathlib

- **Analysis Patterns** (`analysis.py`):
  - Statistical calculation functions (averages, rates, frequencies)
  - DataFrame filtering and aggregation patterns
  - Null-safe calculations

- **Workflow Orchestration** (`workflow.py`):
  - Import patterns for organizing function calls
  - Session state management concepts
  - Filtering and sorting logic

**Adaptations needed:**
- Convert Streamlit UI calls to Plotly Dash callbacks
- Adapt render functions to Dash layout components
- Replace st.session_state with Dash dcc.Store components

### New Components Required

**Finance-specific components not in existing codebase:**
- **Hierarchical Category Parser**: Parse "/" delimited paths, build parent-child relationships
- **Substring Matcher**: Case-insensitive substring search with priority ordering
- **Transaction Deduplication**: Identify duplicate transactions across imports
- **Category Rollup Calculator**: Aggregate child category spending into parent totals
- **Approval State Manager**: Track and persist approval status with locking
- **Time Period Grouper**: Flexible date-based grouping (day/week/month/quarter/year)
- **Plotly Chart Builders**: Dash-specific visualization components

**Why new components are needed:**
- No existing hierarchical category system in codebase
- Substring matching with priority is domain-specific to finance labeling
- Approval workflow is unique to this use case
- Plotly Dash requires different UI approach than Streamlit

## Technical Approach

### Database (CSV Files)

**File Structure:**
```
src/finance/finance_data/
├── transactions.csv
├── categories.csv
├── label_rules.csv
└── transaction_approvals.csv
```

**Schema Definitions:**

**transactions.csv**
```
transaction_id, date, description, amount, account, original_category, import_date
```
- `transaction_id`: String, unique identifier (hash of date+description+amount)
- `date`: String, YYYY-MM-DD format
- `description`: String, transaction description from bank
- `amount`: Float, negative for expenses, positive for income
- `account`: String, optional account name/number
- `original_category`: String, optional category from bank
- `import_date`: String, ISO timestamp of when imported

**categories.csv**
```
category_id, category_path, parent_path, level, display_name, color
```
- `category_id`: Integer, auto-increment unique ID
- `category_path`: String, full path (e.g., "transportation/car/gas")
- `parent_path`: String, parent category path (empty for root)
- `level`: Integer, nesting depth (0 = root)
- `display_name`: String, human-readable name for last segment
- `color`: String, hex color code for visualization

**label_rules.csv**
```
rule_id, substring, category_path, case_sensitive, priority, enabled
```
- `rule_id`: Integer, auto-increment unique ID
- `substring`: String, text to match in transaction description
- `category_path`: String, full category path to assign
- `case_sensitive`: Boolean, whether matching is case-sensitive
- `priority`: Integer, higher number = checked first
- `enabled`: Boolean, whether rule is active

**transaction_approvals.csv**
```
transaction_id, approved_category, approval_date, approval_method, notes
```
- `transaction_id`: String, FK to transactions
- `approved_category`: String, full category path
- `approval_date`: String, ISO timestamp
- `approval_method`: String, "auto", "manual_edit", "manual_accept"
- `notes`: String, optional user notes

### API (Workflow Layer)

**finance_workflow.py functions (one per user action):**

**Data Import:**
- `import_csv_file(file_path, account_name)`: Parse and store new transactions
- `get_import_history()`: List all import sessions

**Category Management:**
- `create_category(parent_path, display_name, color)`: Add new category
- `update_category(category_id, display_name, color)`: Edit category
- `delete_category(category_id)`: Remove category (check for dependencies)
- `get_category_tree()`: Get hierarchical category structure

**Rule Management:**
- `create_rule(substring, category_path, priority)`: Add matching rule
- `update_rule(rule_id, substring, category_path, priority, enabled)`: Edit rule
- `delete_rule(rule_id)`: Remove rule
- `test_rule(substring, sample_descriptions)`: Preview rule matches

**Transaction Review:**
- `get_pending_transactions(filter_params)`: Get transactions awaiting approval
- `approve_transaction(transaction_id, category_path)`: Approve with category
- `bulk_approve_transactions(transaction_ids, category_path)`: Approve multiple
- `edit_transaction_category(transaction_id, new_category_path)`: Change and approve

**Analysis:**
- `get_spending_by_period(start_date, end_date, group_by)`: Time series data
- `get_spending_by_category(start_date, end_date, level)`: Category breakdown
- `get_period_comparison(period1, period2)`: Period-over-period metrics
- `get_category_trends(category_path, num_periods)`: Historical trend data

### Frontend (Plotly Dash)

**finance_app.py structure:**

```python
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go

# Initialize Dash app
app = dash.Dash(__name__)

# Layout with tabs
app.layout = html.Div([
    dcc.Store(id='session-data'),
    dcc.Tabs([
        dcc.Tab(label='Overview', children=render_overview()),
        dcc.Tab(label='Import Data', children=render_import()),
        dcc.Tab(label='Manage Categories', children=render_categories()),
        dcc.Tab(label='Manage Rules', children=render_rules()),
        dcc.Tab(label='Review Transactions', children=render_review()),
        dcc.Tab(label='Detailed Analysis', children=render_analysis()),
    ])
])

# Callbacks for interactivity
@app.callback(...)
def update_chart(...):
    # Chart update logic
    pass
```

**Key Dash Components:**
- `dcc.Upload`: CSV file upload
- `dcc.DatePickerRange`: Date range filter
- `dcc.Dropdown`: Category filter with hierarchy
- `dcc.Graph`: Plotly charts
- `dash_table.DataTable`: Transaction table
- `dcc.Store`: Client-side data storage
- `html.Button`: Action buttons (approve, create, delete)

### Testing

**Test Structure:**
```
tests/finance/
├── test_finance_db.py
├── test_finance_logic.py
├── test_finance_analysis.py
└── test_finance_workflow.py
```

**Focus Areas:**

**test_finance_logic.py:**
- Hierarchical category parsing ("a/b/c" → parent/child relationships)
- Substring matching with priority ordering
- Transaction deduplication logic
- Category path validation

**test_finance_analysis.py:**
- Time-based grouping (day/week/month aggregations)
- Category rollup calculations (parent includes children)
- Period-over-period comparison math
- Null-safe statistical calculations

**test_finance_db.py:**
- CSV loading with correct schemas
- Transaction ID uniqueness enforcement
- Approval persistence across saves
- Category hierarchy integrity

**test_finance_workflow.py:**
- Import workflow (parse → auto-label → store)
- Approval workflow (pending → approved → locked)
- Rule application order (priority-based matching)

**Sample Test Data:**
- 50 sample transactions covering various categories
- 10 sample categories with 2-3 nesting levels
- 15 sample substring rules with different priorities
- Mix of approved and pending transactions

## Implementation Order

### Phase 1: Core Data Layer (Week 1)
1. Set up project structure and CSV schemas
2. Implement `finance_db.py` with CRUD operations
3. Create sample data files
4. Write database tests

### Phase 2: Business Logic (Week 1-2)
5. Implement hierarchical category parsing in `finance_logic.py`
6. Build substring matcher with priority ordering
7. Create transaction deduplication logic
8. Write logic tests

### Phase 3: Analysis Engine (Week 2)
9. Implement time-based grouping in `finance_analysis.py`
10. Build category rollup aggregations
11. Create period comparison calculations
12. Write analysis tests

### Phase 4: Workflow Orchestration (Week 2-3)
13. Implement workflow functions in `finance_workflow.py`
14. Connect workflow to logic and database layers
15. Add error handling and validation
16. Write workflow tests

### Phase 5: Dash Frontend (Week 3-4)
17. Create basic Dash app structure in `finance_app.py`
18. Implement Import Data tab with CSV upload
19. Build Manage Categories tab with CRUD interface
20. Create Manage Rules tab with rule configuration
21. Implement Review Transactions tab with approval workflow
22. Build Overview tab with key metrics and charts
23. Add Detailed Analysis tab with advanced filtering

### Phase 6: Visualizations (Week 4-5)
24. Create time series line chart component
25. Build category breakdown pie chart
26. Implement stacked bar chart for categories over time
27. Add treemap for hierarchical visualization
28. Create comparison charts with period-over-period
29. Wire up all chart interactions and filters

### Phase 7: Polish & Testing (Week 5)
30. Add error handling and user feedback
31. Implement theme toggle
32. Optimize performance for large datasets
33. User acceptance testing
34. Documentation and deployment guide

## Out of Scope

**Not included in initial version:**
- Budget tracking and alerts
- Recurring transaction detection
- Machine learning for improved auto-labeling
- Multi-user support with authentication
- Mobile app or responsive mobile optimization
- Export to PDF/Excel reports
- Bank API integration (only CSV import)
- Forecasting or predictive analytics
- Receipt image upload and OCR
- Split transactions (partial amounts to different categories)
- Multi-currency support
- Investment/portfolio tracking

**Future enhancements to consider:**
- Budget vs actual tracking with alerts
- Recurring transaction patterns (auto-detect subscriptions)
- Machine learning model trained on approved labels
- Shared household budgets with role-based access
- Mobile-responsive design improvements
- Scheduled report generation (email weekly summary)
- Direct bank connection via Plaid or similar
- Time-series forecasting for spending trends

## Success Criteria

**Core Functionality:**
- User can import a CSV file and see transactions in the system
- User can create nested categories (e.g., "food/restaurants/italian")
- User can define substring rules that correctly auto-label transactions
- User can approve auto-labeled transactions and labels persist
- User can view spending over time grouped by month
- Category rollups work correctly (parent includes all children)

**Performance:**
- Dashboard loads in under 3 seconds
- Chart updates happen in under 2 seconds
- CSV import of 1000 transactions completes in under 5 seconds

**User Experience:**
- User can complete full workflow (import → review → analyze) without documentation
- Error messages are clear and actionable
- No data loss occurs during normal operations
- Approved labels never get overwritten unexpectedly

**Code Quality:**
- All files have docstrings and inline comments explaining business logic
- Each file includes standalone test section (if __name__ == "__main__")
- Clear separation of concerns across layers (_db, _logic, _analysis, _workflow, _app)
- Meaningful variable names following conventions (_df suffix for DataFrames)

**Validation Metrics:**
- Successfully import and categorize 500 real transactions
- Create 20+ categories with 3+ levels of nesting
- Define 30+ substring rules with correct priority ordering
- 95%+ of transactions auto-labeled correctly with good rules
- Zero bugs in approval persistence logic
- All charts render correctly with various date ranges and filters
