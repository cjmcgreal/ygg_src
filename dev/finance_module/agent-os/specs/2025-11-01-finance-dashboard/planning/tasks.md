# Task Breakdown: Finance Dashboard

## Overview
Total Task Groups: 10
Complexity: High - Novel hierarchical category system, approval workflow, and Plotly Dash integration
Estimated Timeline: 5 weeks

## Specialist Role Assignments

Since this is a Python prototype project following the Python Prototype Development Standards, tasks are organized by layer rather than traditional full-stack roles:

- **Database Engineer**: CSV database layer, schema design, data integrity
- **Backend Engineer**: Business logic, workflow orchestration, core algorithms
- **Data Analyst**: Analysis functions, aggregations, statistical calculations
- **Frontend Engineer**: Plotly Dash UI, visualizations, user interactions
- **Testing Engineer**: Test strategy, integration testing, test data creation

## Task List

### Phase 1: Foundation & Database Layer

#### Task Group 1: Project Setup & CSV Database Schema
**Assigned implementer:** database-engineer
**Dependencies:** None
**Complexity:** [Small]

- [ ] 1.0 Complete project foundation and database layer
  - [ ] 1.1 Create directory structure
    - Create `src/finance/` directory
    - Create `src/finance/finance_data/` directory for CSV files
    - Create `tests/finance/` directory mirroring src structure
    - Create root `requirements.txt` file
  - [ ] 1.2 Define CSV schemas and create template files
    - Create `transactions.csv` with schema: transaction_id, date, description, amount, account, original_category, import_date
    - Create `categories.csv` with schema: category_id, category_path, parent_path, level, display_name, color
    - Create `label_rules.csv` with schema: rule_id, substring, category_path, case_sensitive, priority, enabled
    - Create `transaction_approvals.csv` with schema: transaction_id, approved_category, approval_date, approval_method, notes
    - Add header rows to all CSV files
  - [ ] 1.3 Set up requirements.txt
    - Add: plotly (for visualizations)
    - Add: dash (for web framework)
    - Add: pandas (for data manipulation)
    - Add: pytest (for testing)
    - Pin versions for reproducibility
  - [ ] 1.4 Write 2-8 focused tests for finance_db.py (to be implemented in Task 1.5)
    - Test: load_transactions() returns DataFrame with correct schema
    - Test: save_transactions() persists data correctly to CSV
    - Test: load_categories() handles empty file gracefully
    - Test: transaction_id uniqueness is enforced
    - Test: datetime columns are parsed correctly
    - Limit to testing critical database operations only
  - [ ] 1.5 Implement finance_db.py - CSV database interface
    - Function: `load_transactions()` - Load transactions.csv into DataFrame
    - Function: `save_transactions(df)` - Save transactions DataFrame to CSV
    - Function: `load_categories()` - Load categories.csv into DataFrame
    - Function: `save_categories(df)` - Save categories DataFrame to CSV
    - Function: `load_label_rules()` - Load label_rules.csv into DataFrame
    - Function: `save_label_rules(df)` - Save rules DataFrame to CSV
    - Function: `load_transaction_approvals()` - Load approvals.csv into DataFrame
    - Function: `save_transaction_approvals(df)` - Save approvals DataFrame to CSV
    - Function: `get_schema(table_name)` - Return expected column names and types
    - Handle datetime column conversion (date, import_date, approval_date)
    - Use pathlib for directory path management
    - Reuse patterns from procedures-app database.py
    - Add comprehensive docstrings explaining each function
    - Add `if __name__ == "__main__":` section with example usage
  - [ ] 1.6 Ensure database layer tests pass
    - Run ONLY the 2-8 tests written in 1.4
    - Verify CSV files can be created, read, and written
    - Verify schema validation works correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 database tests pass
- CSV files load and save without errors
- Schema validation enforces correct column structure
- Datetime columns parse correctly
- Directory structure follows Python prototype standards

---

### Phase 2: Business Logic Layer

#### Task Group 2: Core Business Logic - Category Hierarchy & Substring Matching
**Assigned implementer:** backend-engineer
**Dependencies:** Task Group 1
**Complexity:** [Large]

- [ ] 2.0 Complete business logic layer
  - [ ] 2.1 Write 2-8 focused tests for finance_logic.py core functions
    - Test: parse_category_path("food/restaurants/italian") returns correct components
    - Test: get_parent_path("food/restaurants/italian") returns "food/restaurants"
    - Test: calculate_category_level("food/restaurants") returns 1
    - Test: match_substring_rule("STARBUCKS STORE #123", rules_df) returns correct category with priority
    - Test: validate_category_path("food/restaurants") returns True for valid path
    - Test: generate_transaction_id(date, description, amount) creates consistent hash
    - Limit to core logic functions only
  - [ ] 2.2 Implement hierarchical category parser functions
    - Function: `parse_category_path(category_path)` - Split path by "/" into segments
    - Function: `get_parent_path(category_path)` - Extract parent from full path (empty string for root)
    - Function: `get_category_name(category_path)` - Extract last segment as display name
    - Function: `calculate_category_level(category_path)` - Count "/" to determine nesting depth (0 = root)
    - Function: `build_category_tree(categories_df)` - Convert flat DataFrame to nested dict structure
    - Function: `get_all_children(category_path, categories_df)` - Recursively find all descendant categories
    - Handle edge cases: empty paths, single-level categories, deep nesting
    - Add docstrings explaining hierarchy logic
  - [ ] 2.3 Implement substring matching engine with priority
    - Function: `match_substring_rule(description, rules_df)` - Find first matching rule by priority
    - Sort rules by priority (descending) before matching
    - Case-insensitive matching by default (configurable via case_sensitive flag)
    - Return matched rule info: category_path, rule_id, substring matched
    - Return None if no match found
    - Filter out disabled rules before matching
    - Add docstring explaining priority-based matching logic
  - [ ] 2.4 Implement transaction deduplication logic
    - Function: `generate_transaction_id(date, description, amount)` - Create hash-based unique ID
    - Use consistent hashing algorithm (e.g., SHA256 of concatenated fields)
    - Function: `find_duplicates(new_transactions_df, existing_transactions_df)` - Identify duplicates by transaction_id
    - Return DataFrame of duplicate transactions
    - Add docstring explaining deduplication strategy
  - [ ] 2.5 Implement approval state manager
    - Function: `is_transaction_approved(transaction_id, approvals_df)` - Check approval status
    - Function: `get_approved_category(transaction_id, approvals_df)` - Get approved category or None
    - Function: `create_approval(transaction_id, category_path, method)` - Create new approval record
    - Approval methods: "auto", "manual_edit", "manual_accept"
    - Add timestamp automatically to approval_date
    - Add docstring explaining approval locking behavior
  - [ ] 2.6 Implement category validation
    - Function: `validate_category_path(category_path, categories_df)` - Check if category exists
    - Function: `validate_category_hierarchy(categories_df)` - Check for orphaned children
    - Function: `can_delete_category(category_id, transactions_df, rules_df)` - Check for dependencies
    - Return validation errors with clear messages
    - Add docstring explaining validation rules
  - [ ] 2.7 Add if __name__ == "__main__" section
    - Show examples of parsing "food/restaurants/italian"
    - Demonstrate substring matching with sample rules
    - Show transaction ID generation
    - Show approval checking workflow
  - [ ] 2.8 Ensure business logic tests pass
    - Run ONLY the 2-8 tests written in 2.1
    - Verify category hierarchy parsing works correctly
    - Verify substring matching respects priority order
    - Verify transaction ID generation is consistent
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 business logic tests pass
- Category hierarchy parser handles arbitrary nesting depth
- Substring matching correctly prioritizes rules
- Transaction IDs are unique and deterministic
- Approval state tracking prevents overwrites
- Category validation catches hierarchy errors

---

### Phase 3: Analysis & Aggregation Layer

#### Task Group 3: Data Analysis Functions
**Assigned implementer:** data-analyst
**Dependencies:** Task Groups 1-2
**Complexity:** [Medium]

- [ ] 3.0 Complete data analysis layer
  - [ ] 3.1 Write 2-8 focused tests for finance_analysis.py
    - Test: group_by_period(transactions_df, "month") returns monthly aggregations
    - Test: calculate_category_rollup(transactions_df, categories_df, "food") includes all subcategories
    - Test: calculate_period_comparison(period1_df, period2_df) returns correct growth percentages
    - Test: calculate_moving_average(transactions_df, window=3) computes correctly
    - Test: filter_by_date_range(transactions_df, start, end) returns correct subset
    - Limit to critical analysis functions only
  - [ ] 3.2 Implement time-based grouping functions
    - Function: `group_by_period(transactions_df, period_type)` - Aggregate by day/week/month/quarter/year
    - Use pandas resample or groupby with appropriate frequency
    - Return DataFrame with period labels and aggregated amounts
    - Handle income vs expense separately (positive vs negative amounts)
    - Period types: "day", "week", "month", "quarter", "year"
    - Add docstring explaining grouping logic
  - [ ] 3.3 Implement category rollup aggregations
    - Function: `calculate_category_rollup(transactions_df, categories_df, category_path)` - Sum all children
    - Get all descendant categories using logic from finance_logic.py
    - Sum transaction amounts for parent and all children
    - Return nested structure with category totals and subtotals
    - Handle approved and pending transactions separately
    - Add docstring explaining rollup calculation
  - [ ] 3.4 Implement period-over-period comparison
    - Function: `calculate_period_comparison(period1_df, period2_df)` - Compare two periods
    - Calculate absolute difference and percentage change
    - Handle division by zero gracefully
    - Return comparison metrics: total_change, percent_change, period1_total, period2_total
    - Add docstring explaining comparison logic
  - [ ] 3.5 Implement statistical calculations
    - Function: `calculate_moving_average(transactions_df, window)` - Rolling average over time
    - Function: `calculate_summary_stats(transactions_df)` - Total, mean, median, std dev
    - Function: `get_top_categories(transactions_df, n)` - Top N spending categories
    - All calculations should be null-safe (handle empty DataFrames)
    - Reuse patterns from procedures-app analysis.py
    - Add docstrings explaining statistical methods
  - [ ] 3.6 Implement filtering helpers
    - Function: `filter_by_date_range(transactions_df, start_date, end_date)` - Date range filter
    - Function: `filter_by_category(transactions_df, category_path, include_children)` - Category filter
    - Function: `filter_by_amount_range(transactions_df, min_amount, max_amount)` - Amount filter
    - Function: `filter_by_approval_status(transactions_df, approvals_df, status)` - Approval filter
    - Status options: "approved", "pending", "all"
    - Return filtered DataFrames with original indexes preserved
    - Add docstrings explaining filter behavior
  - [ ] 3.7 Add if __name__ == "__main__" section
    - Show example of monthly grouping with sample data
    - Demonstrate category rollup calculation
    - Show period comparison calculation
    - Display summary statistics
  - [ ] 3.8 Ensure analysis layer tests pass
    - Run ONLY the 2-8 tests written in 3.1
    - Verify time-based grouping produces correct periods
    - Verify category rollups include all children
    - Verify period comparisons calculate correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 analysis tests pass
- Time-based grouping works for all period types (day/week/month/quarter/year)
- Category rollups correctly aggregate parent and all children
- Period comparisons handle edge cases (zero values, negative values)
- Filters can be combined to create complex queries
- All calculations are null-safe and handle empty DataFrames

---

### Phase 4: Workflow Orchestration Layer

#### Task Group 4: Workflow Functions - Orchestration
**Assigned implementer:** backend-engineer
**Dependencies:** Task Groups 1-3
**Complexity:** [Large]

- [ ] 4.0 Complete workflow orchestration layer
  - [ ] 4.1 Write 2-8 focused tests for finance_workflow.py
    - Test: import_csv_file(file_path) returns import summary with transaction count
    - Test: import applies auto-labeling rules correctly
    - Test: approve_transaction(transaction_id, category) creates approval record
    - Test: approved labels persist and aren't overwritten on re-import
    - Test: create_category(parent, name, color) adds to hierarchy correctly
    - Test: get_pending_transactions() returns only unapproved transactions
    - Limit to critical workflow integration tests only
  - [ ] 4.2 Implement data import workflows
    - Function: `import_csv_file(file_path, account_name)` - Full import orchestration
    - Steps: Parse CSV → Generate transaction IDs → Check duplicates → Apply auto-labeling → Save transactions
    - Return import summary: new_count, duplicate_count, auto_labeled_count
    - Function: `parse_csv_format(file_path)` - Detect CSV structure and map columns
    - Handle common bank CSV formats (varying column names)
    - Function: `get_import_history()` - List all import sessions with timestamps
    - Add error handling for malformed CSV files
    - Add docstrings explaining import workflow steps
  - [ ] 4.3 Implement auto-labeling workflow
    - Function: `apply_auto_labels(transactions_df, rules_df)` - Apply rules to unlabeled transactions
    - Skip already-approved transactions (check approvals first)
    - For each unlabeled transaction, find matching rule using finance_logic.py
    - Create auto-approval records with method="auto"
    - Return labeled_df with new category assignments
    - Function: `bulk_apply_rules(rule_id)` - Re-apply specific rule to all matching transactions
    - Add docstring explaining auto-labeling logic and approval preservation
  - [ ] 4.4 Implement category management workflows
    - Function: `create_category(parent_path, display_name, color)` - Add new category
    - Generate category_path by joining parent_path and display_name
    - Calculate level from parent
    - Validate parent exists
    - Add to categories_df and save
    - Function: `update_category(category_id, display_name, color)` - Edit category
    - Update category while preserving hierarchy relationships
    - Function: `delete_category(category_id)` - Remove category
    - Check for dependencies (transactions, rules, child categories)
    - Return error if dependencies exist
    - Function: `get_category_tree()` - Get hierarchical structure for UI display
    - Return nested dict or list suitable for tree view component
    - Add docstrings explaining category management rules
  - [ ] 4.5 Implement rule management workflows
    - Function: `create_rule(substring, category_path, priority, case_sensitive)` - Add matching rule
    - Validate category exists
    - Set enabled=True by default
    - Function: `update_rule(rule_id, **kwargs)` - Edit rule properties
    - Allow updating substring, category_path, priority, enabled, case_sensitive
    - Function: `delete_rule(rule_id)` - Remove rule
    - Function: `test_rule(substring, sample_descriptions)` - Preview matches
    - Return list of sample descriptions that would match
    - Add docstrings explaining rule configuration
  - [ ] 4.6 Implement transaction review workflows
    - Function: `get_pending_transactions(filter_params)` - Get unapproved transactions
    - Apply filters: date_range, amount_range, has_auto_label
    - Sort by amount (descending) or date
    - Return DataFrame ready for review UI
    - Function: `approve_transaction(transaction_id, category_path)` - Approve with category
    - Validate category exists
    - Create approval record with method="manual_accept" if accepting auto-label, or "manual_edit" if changing
    - Function: `bulk_approve_transactions(transaction_ids, category_path)` - Approve multiple
    - Apply same approval logic to list of transaction IDs
    - Return summary: approved_count, error_count
    - Function: `edit_transaction_category(transaction_id, new_category_path)` - Change and approve
    - Update category and create approval with method="manual_edit"
    - Add docstrings explaining approval workflow and locking behavior
  - [ ] 4.7 Implement analysis workflows
    - Function: `get_spending_by_period(start_date, end_date, group_by)` - Time series data
    - Load transactions, filter by date range, group by period, calculate totals
    - Return DataFrame formatted for time series chart
    - Function: `get_spending_by_category(start_date, end_date, level)` - Category breakdown
    - Load transactions, filter by date, calculate category rollups
    - Option to show specific hierarchy level or all levels
    - Return DataFrame formatted for pie/bar charts
    - Function: `get_period_comparison(period1_start, period1_end, period2_start, period2_end)` - Compare periods
    - Calculate totals for each period, compute comparisons
    - Return comparison metrics for dashboard display
    - Function: `get_category_trends(category_path, num_periods, period_type)` - Historical trends
    - Get spending for category over last N periods (months, quarters, etc.)
    - Include rollup of child categories
    - Return time series data for trend visualization
    - Add docstrings explaining analysis orchestration
  - [ ] 4.8 Add if __name__ == "__main__" section
    - Show example of full import workflow with sample CSV
    - Demonstrate category creation and hierarchy
    - Show auto-labeling and approval workflow
    - Display analysis workflow with sample queries
  - [ ] 4.9 Ensure workflow layer tests pass
    - Run ONLY the 2-8 tests written in 4.1
    - Verify import workflow completes successfully
    - Verify auto-labeling preserves approved labels
    - Verify approval workflow locks categories correctly
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 workflow tests pass
- Import workflow successfully parses CSV, deduplicates, and auto-labels
- Auto-labeling never overwrites approved labels
- Category management maintains hierarchy integrity
- Rule management allows priority-based configuration
- Transaction approval workflow prevents accidental overwrites
- Analysis workflows return data formatted for visualization

---

### Phase 5: Dash Application Foundation

#### Task Group 5: Dash App Structure & Basic UI
**Assigned implementer:** frontend-engineer
**Dependencies:** Task Groups 1-4
**Complexity:** [Medium]

- [ ] 5.0 Complete Dash application foundation
  - [ ] 5.1 Write 2-8 focused tests for finance_app.py basic structure
    - Test: app initializes without errors
    - Test: app.layout contains expected tab structure
    - Test: render_overview() returns valid Dash components
    - Test: render_import() returns valid Dash components
    - Test: theme toggle callback updates stored theme value
    - Limit to structural and initialization tests only
  - [ ] 5.2 Create basic Dash app structure
    - Import required Dash components: dash, dcc, html, Input, Output, State
    - Initialize Dash app with external stylesheets (modern theme)
    - Define app.layout with dcc.Tabs for main navigation
    - Create dcc.Store components for session data: theme, selected_date_range, selected_categories
    - Set up app.run_server() in if __name__ == "__main__" section
    - Add comprehensive docstrings explaining app structure
  - [ ] 5.3 Create tab structure and navigation
    - Tab 1: Overview (render_overview())
    - Tab 2: Import Data (render_import())
    - Tab 3: Manage Categories (render_categories())
    - Tab 4: Manage Rules (render_rules())
    - Tab 5: Review Transactions (render_review())
    - Tab 6: Detailed Analysis (render_analysis())
    - Each render function returns html.Div with tab content
    - Add tab icons using Dash Bootstrap Icons or similar
  - [ ] 5.4 Implement theme toggle
    - Add theme toggle button in app header
    - Store theme preference in dcc.Store(id='theme-store')
    - Create callback to update CSS class based on theme
    - Support "light" and "dark" themes
    - Use Dash Bootstrap Components theming if available
  - [ ] 5.5 Create reusable UI components
    - Component: `create_metric_card(title, value, change_percent)` - Metric display card
    - Component: `create_filter_panel(show_date, show_category, show_amount)` - Filter controls
    - Component: `create_data_table(df, columns, id_prefix)` - Styled data table
    - Component: `create_page_header(title, subtitle, actions)` - Page header with title and action buttons
    - Return Dash html/dcc components from each function
    - Add docstrings explaining component usage
  - [ ] 5.6 Set up error handling and loading states
    - Create error message component: `display_error(message)`
    - Create loading spinner: wrap components in dcc.Loading
    - Create toast notifications for success/error messages
    - Add try-except blocks in callbacks with user-friendly error messages
  - [ ] 5.7 Add if __name__ == "__main__" section
    - Initialize app
    - Run server on debug mode
    - Print URL for accessing app
  - [ ] 5.8 Ensure basic app structure tests pass
    - Run ONLY the 2-8 tests written in 5.1
    - Verify app initializes without errors
    - Verify all tabs are present in layout
    - Verify theme toggle works
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 app structure tests pass
- Dash app initializes and runs without errors
- All six tabs are accessible via navigation
- Theme toggle switches between light and dark modes
- Reusable components render correctly
- Error handling displays user-friendly messages
- App follows Python prototype standards (render functions, clear structure)

---

### Phase 6: Dash UI Implementation - Data Management Tabs

#### Task Group 6: Import Data & Category Management UIs
**Assigned implementer:** frontend-engineer
**Dependencies:** Task Group 5
**Complexity:** [Medium]

- [ ] 6.0 Complete data management UI tabs
  - [ ] 6.1 Write 2-8 focused tests for data management tabs
    - Test: CSV upload component triggers import callback
    - Test: import callback returns success message after file upload
    - Test: import history table displays after successful import
    - Test: category tree displays existing categories
    - Test: create category form validation works correctly
    - Limit to critical UI interaction tests only
  - [ ] 6.2 Implement Import Data tab (render_import)
    - Add dcc.Upload component for CSV file upload
    - Display upload instructions (expected CSV format)
    - Show import progress indicator during processing
    - Display import summary after completion (new transactions, duplicates, auto-labeled)
    - Create import history table showing past imports with timestamps
    - Add callback: @app.callback(Output('import-result'), Input('upload-data', 'contents'))
    - Callback logic: Parse uploaded file → Call finance_workflow.import_csv_file() → Display results
    - Add error handling for invalid CSV formats
    - Add docstrings explaining import UI workflow
  - [ ] 6.3 Implement Manage Categories tab (render_categories)
    - Display category hierarchy as expandable tree view
    - Use dash_treeview or custom nested html.Ul/html.Li structure
    - Show category path, display name, and color for each category
    - Add "Create New Category" form with fields: parent dropdown, display name input, color picker
    - Add edit button for each category (opens modal with edit form)
    - Add delete button for each category (shows confirmation, checks dependencies)
    - Create callbacks for CRUD operations:
      - @app.callback to create category: calls finance_workflow.create_category()
      - @app.callback to update category: calls finance_workflow.update_category()
      - @app.callback to delete category: calls finance_workflow.delete_category()
    - Display success/error messages after each operation
    - Refresh category tree after modifications
    - Add docstrings explaining category management UI
  - [ ] 6.4 Implement Manage Rules tab (render_rules)
    - Display rules table with columns: priority, substring, category, case_sensitive, enabled, actions
    - Sort table by priority (descending) by default
    - Add "Create New Rule" form with fields: substring input, category dropdown, priority input, case_sensitive checkbox
    - Add edit button for each rule (inline editing or modal)
    - Add enable/disable toggle for each rule
    - Add delete button for each rule
    - Add "Test Rule" button that opens modal with sample description input
    - Create callbacks for rule operations:
      - @app.callback to create rule: calls finance_workflow.create_rule()
      - @app.callback to update rule: calls finance_workflow.update_rule()
      - @app.callback to delete rule: calls finance_workflow.delete_rule()
      - @app.callback to test rule: calls finance_workflow.test_rule()
    - Display rule test results in modal showing matching descriptions
    - Add docstrings explaining rule management UI
  - [ ] 6.5 Add if __name__ == "__main__" section
    - Not applicable for UI-only file, but ensure file can be imported without errors
  - [ ] 6.6 Ensure data management UI tests pass
    - Run ONLY the 2-8 tests written in 6.1
    - Verify CSV upload triggers import workflow
    - Verify category CRUD operations update UI correctly
    - Verify rule management updates rules table
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 data management UI tests pass
- CSV upload successfully imports transactions and displays summary
- Import history shows past import sessions
- Category tree displays hierarchical structure correctly
- Category CRUD operations work without errors
- Rule management allows priority-based configuration
- Rule testing shows preview of matching transactions
- All forms include validation and error messages

---

### Phase 7: Dash UI Implementation - Transaction Review & Dashboard

#### Task Group 7: Review Transactions & Dashboard Tabs
**Assigned implementer:** frontend-engineer
**Dependencies:** Task Group 6
**Complexity:** [Large]

- [ ] 7.0 Complete transaction review and dashboard UI
  - [ ] 7.1 Write 2-8 focused tests for review and dashboard tabs
    - Test: pending transactions table loads correctly
    - Test: approve button creates approval record
    - Test: edit category updates transaction and approves
    - Test: dashboard metrics display correct values
    - Test: date range filter updates displayed transactions
    - Limit to critical user workflow tests only
  - [ ] 7.2 Implement Review Transactions tab (render_review)
    - Add filter panel: date range picker, "show approved" checkbox, amount range slider
    - Display pending transactions table with columns: date, description, amount, auto_label, actions
    - Sort by amount (descending) by default
    - Add "Approve" button for each transaction (green checkmark icon)
    - Add "Edit Category" button for each transaction (pencil icon, opens dropdown)
    - Add bulk action controls: "Select All", "Approve Selected", bulk category dropdown
    - Add pagination or virtual scrolling for large transaction lists
    - Highlight auto-labeled transactions with visual indicator
    - Create callbacks:
      - @app.callback to load pending transactions: calls finance_workflow.get_pending_transactions()
      - @app.callback to approve transaction: calls finance_workflow.approve_transaction()
      - @app.callback to edit category: calls finance_workflow.edit_transaction_category()
      - @app.callback for bulk approve: calls finance_workflow.bulk_approve_transactions()
    - Update table after approval actions
    - Add success messages: "Transaction approved", "5 transactions approved"
    - Add docstrings explaining review workflow UI
  - [ ] 7.3 Implement Overview tab (render_overview) - Metrics Section
    - Display key metrics in card layout:
      - Total spending this month (with vs last month comparison)
      - Total income this month (with vs last month comparison)
      - Top spending category this month
      - Number of pending transactions awaiting review
    - Use create_metric_card() component for consistent styling
    - Add date range selector for metrics (default: current month)
    - Create callback to update metrics based on date selection:
      - @app.callback: calls finance_workflow.get_period_comparison()
      - Calculate month-over-month changes
      - Format values as currency with proper negative/positive indicators
    - Add docstrings explaining metrics calculation
  - [ ] 7.4 Implement Overview tab - Primary Time Series Chart
    - Add time series line chart showing spending over time
    - Use dcc.Graph with plotly.graph_objects
    - Chart features:
      - X-axis: date (grouped by selected period)
      - Y-axis: amount
      - Two lines: expenses (red) and income (green)
      - Hover tooltips showing date, amount, transaction count
    - Add period grouping selector: day, week, month, quarter, year (dropdown above chart)
    - Create callback to update chart:
      - @app.callback(Output('overview-timeseries'), Input('period-selector', 'value'))
      - Calls finance_workflow.get_spending_by_period()
      - Builds plotly figure with go.Scatter traces
    - Add zoom/pan interactions (plotly default)
    - Add docstrings explaining time series visualization
  - [ ] 7.5 Implement Overview tab - Top Categories Chart
    - Add horizontal bar chart showing top 10 spending categories
    - Use dcc.Graph with plotly.graph_objects
    - Chart features:
      - X-axis: spending amount
      - Y-axis: category names
      - Bars colored by category color from categories.csv
      - Hover tooltips showing category, amount, percentage of total
    - Create callback to update chart:
      - @app.callback: calls finance_workflow.get_spending_by_category()
      - Sorts by amount descending
      - Limits to top 10
    - Make bars clickable to drill down to subcategories
    - Add docstrings explaining category breakdown visualization
  - [ ] 7.6 Implement Detailed Analysis tab (render_analysis)
    - Add comprehensive filter panel:
      - Date range picker (start and end date)
      - Category multi-select dropdown (with hierarchy)
      - Amount range slider (min and max)
      - Approval status filter: all, approved, pending
      - "Apply Filters" button
    - Display filtered transactions table with all columns
    - Add export button to download filtered data as CSV
    - Create callback to apply filters and update table:
      - @app.callback: calls multiple finance_analysis.py filter functions
      - Chains filters together
      - Updates table with filtered results
    - Add summary statistics for filtered data: count, total, average, median
    - Add docstrings explaining advanced filtering UI
  - [ ] 7.7 Add if __name__ == "__main__" section
    - Not applicable for UI-only file
  - [ ] 7.8 Ensure review and dashboard UI tests pass
    - Run ONLY the 2-8 tests written in 7.1
    - Verify transaction approval workflow works end-to-end
    - Verify dashboard metrics display correctly
    - Verify charts render with sample data
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 review and dashboard UI tests pass
- Transaction review table displays pending transactions correctly
- Approval actions update transaction status immediately
- Bulk approval operations work correctly
- Overview dashboard displays accurate metrics and comparisons
- Time series chart shows spending trends over time
- Category breakdown chart shows top spending areas
- Detailed analysis tab allows complex filtering
- All charts are interactive with zoom, pan, and hover tooltips

---

### Phase 8: Advanced Visualizations

#### Task Group 8: Additional Charts & Interactions
**Assigned implementer:** frontend-engineer
**Dependencies:** Task Group 7
**Complexity:** [Medium]

- [ ] 8.0 Complete advanced visualization features
  - [ ] 8.1 Write 2-8 focused tests for advanced visualizations
    - Test: stacked area chart renders with multiple categories
    - Test: treemap chart displays hierarchical categories
    - Test: period comparison chart shows correct growth indicators
    - Test: chart drill-down interaction filters data correctly
    - Limit to critical visualization tests only
  - [ ] 8.2 Create stacked area chart for category spending over time
    - Add to Detailed Analysis tab
    - Chart shows spending by top N categories over time as stacked areas
    - X-axis: date (grouped by month)
    - Y-axis: cumulative spending amount
    - Each category gets distinct color (from categories.csv)
    - Legend shows category names with toggles
    - Hover shows breakdown by category for that time period
    - Create callback:
      - @app.callback: calls finance_workflow.get_spending_by_category() for each period
      - Builds go.Scatter with fill='tonexty' for stacking effect
    - Add docstrings explaining stacked visualization logic
  - [ ] 8.3 Create treemap for hierarchical category visualization
    - Add to Overview or Detailed Analysis tab
    - Use plotly.graph_objects.Treemap
    - Display entire category hierarchy with proportional sizing
    - Click on category to zoom into subcategories
    - Color code by category (use colors from categories.csv)
    - Hover shows category path, amount, percentage
    - Create callback:
      - @app.callback: calls finance_workflow.get_spending_by_category(level='all')
      - Formats data for treemap: labels, parents, values
      - Builds treemap figure
    - Add docstrings explaining treemap data structure
  - [ ] 8.4 Create period comparison bar chart
    - Add to Overview tab
    - Show side-by-side bars comparing this month vs last month for top categories
    - X-axis: category names
    - Y-axis: spending amount
    - Two bars per category: current period (blue), previous period (gray)
    - Add growth indicators: green up arrow, red down arrow, percentage change label
    - Create callback:
      - @app.callback: calls finance_workflow.get_period_comparison()
      - Builds grouped bar chart with go.Bar traces
    - Add docstrings explaining comparison visualization
  - [ ] 8.5 Implement chart drill-down interactions
    - Make category pie chart clickable
    - On click: update URL or dcc.Store with selected category
    - Show filtered transactions for clicked category in table below chart
    - Add "Back to all categories" button to reset filter
    - Create callback chain:
      - @app.callback(Output('selected-category-store'), Input('category-chart', 'clickData'))
      - @app.callback(Output('transactions-table'), Input('selected-category-store', 'data'))
    - Highlight selected category in chart
    - Add docstrings explaining drill-down interaction
  - [ ] 8.6 Add moving average trend line to time series
    - Add optional moving average overlay to main time series chart
    - Checkbox control: "Show 3-month moving average"
    - Dashed line overlay on time series chart
    - Use finance_analysis.calculate_moving_average()
    - Update time series callback to conditionally add moving average trace
    - Add docstrings explaining trend line calculation
  - [ ] 8.7 Add if __name__ == "__main__" section
    - Not applicable for UI-only file
  - [ ] 8.8 Ensure advanced visualization tests pass
    - Run ONLY the 2-8 tests written in 8.1
    - Verify stacked area chart renders correctly
    - Verify treemap displays hierarchy
    - Verify period comparison shows growth indicators
    - Do NOT run entire test suite at this stage

**Acceptance Criteria:**
- All 2-8 advanced visualization tests pass
- Stacked area chart shows category spending trends over time
- Treemap visualizes entire category hierarchy proportionally
- Period comparison chart clearly shows month-over-month changes
- Chart drill-down allows clicking categories to filter transactions
- Moving average trend line option works correctly
- All charts maintain consistent color scheme from category definitions
- Charts are responsive and performant with real data

---

### Phase 9: Integration, Sample Data & End-to-End Testing

#### Task Group 9: Integration Testing & Sample Data
**Assigned implementer:** testing-engineer
**Dependencies:** Task Groups 1-8
**Complexity:** [Medium]

- [ ] 9.0 Review existing tests and create integration tests
  - [ ] 9.1 Review tests from previous task groups
    - Review 2-8 tests from Task Group 1 (database layer)
    - Review 2-8 tests from Task Group 2 (business logic)
    - Review 2-8 tests from Task Group 3 (analysis layer)
    - Review 2-8 tests from Task Group 4 (workflow layer)
    - Review 2-8 tests from Task Group 5 (app structure)
    - Review 2-8 tests from Task Group 6 (data management UI)
    - Review 2-8 tests from Task Group 7 (dashboard UI)
    - Review 2-8 tests from Task Group 8 (advanced visualizations)
    - Total existing tests: approximately 16-64 tests
  - [ ] 9.2 Analyze test coverage gaps for finance dashboard feature
    - Identify critical end-to-end workflows lacking test coverage
    - Focus on integration points between layers (workflow → logic → db)
    - Identify gaps in approval workflow testing (most critical feature)
    - Identify gaps in import workflow testing (key user entry point)
    - Do NOT assess entire application coverage - only this feature
    - Prioritize workflows over individual function coverage
  - [ ] 9.3 Create realistic sample transaction data
    - Create sample CSV file: `sample_transactions.csv` with 100+ transactions
    - Include transactions spanning 6 months
    - Mix of expenses (negative amounts) and income (positive amounts)
    - Realistic descriptions for common categories:
      - Groceries: "WHOLE FOODS #123", "TRADER JOES", "SAFEWAY"
      - Restaurants: "STARBUCKS", "CHIPOTLE", "UBER EATS"
      - Transportation: "SHELL GAS", "UBER TRIP", "BART TICKET"
      - Utilities: "PG&E ELECTRIC", "COMCAST", "WATER DISTRICT"
      - Housing: "RENT PAYMENT", "HOME DEPOT"
    - Include some ambiguous descriptions that need manual review
    - Include some duplicate transactions to test deduplication
    - Save to `src/finance/finance_data/sample_transactions.csv`
  - [ ] 9.4 Create sample category hierarchy
    - Create `sample_categories.csv` with realistic category tree:
      - housing (rent, utilities/electric, utilities/water, utilities/internet)
      - food (groceries, restaurants/coffee, restaurants/fast_food)
      - transportation (car/gas, car/maintenance, public_transit, rideshare)
      - entertainment (streaming, hobbies, events)
      - income (salary, investment, other)
    - Assign distinct colors to each category (hex codes)
    - 20+ total categories with 2-3 levels of nesting
    - Save to `src/finance/finance_data/sample_categories.csv`
  - [ ] 9.5 Create sample label rules
    - Create `sample_label_rules.csv` with 15+ realistic rules:
      - "WHOLE FOODS" → "food/groceries", priority: 100
      - "TRADER JOES" → "food/groceries", priority: 100
      - "STARBUCKS" → "food/restaurants/coffee", priority: 100
      - "CHIPOTLE" → "food/restaurants/fast_food", priority: 100
      - "SHELL" → "transportation/car/gas", priority: 90
      - "UBER" → "transportation/rideshare", priority: 80 (lower priority to disambiguate UBER EATS)
      - "UBER EATS" → "food/restaurants", priority: 100
      - "PG&E" → "housing/utilities/electric", priority: 100
      - "RENT" → "housing/rent", priority: 100
    - Include priority conflicts to test priority ordering
    - Save to `src/finance/finance_data/sample_label_rules.csv`
  - [ ] 9.6 Write up to 10 additional integration tests maximum
    - Test: Full import workflow (import → auto-label → deduplicate → save)
      - Import sample_transactions.csv
      - Verify auto-labeling applied rules correctly
      - Verify duplicates were detected
      - Verify import summary is accurate
    - Test: Approval persistence across re-import
      - Import transactions → Approve some manually → Re-import same file
      - Verify approved labels not overwritten
      - Verify unapproved transactions get re-labeled
    - Test: Category rollup calculation end-to-end
      - Import transactions with nested categories
      - Calculate rollup for "food" category
      - Verify total includes groceries + restaurants + subcategories
    - Test: Period comparison workflow
      - Import 6 months of data
      - Compare month 1 vs month 2 spending
      - Verify percentage changes calculate correctly
    - Test: Hierarchical category creation and deletion
      - Create parent category → Create child category
      - Attempt to delete parent with children (should fail)
      - Delete child first, then parent (should succeed)
    - Test: Rule priority conflict resolution
      - Create two rules matching same description with different priorities
      - Verify higher priority rule wins
    - Test: Bulk approval workflow
      - Import transactions → Select multiple pending → Bulk approve with category
      - Verify all selected transactions get approved
    - Test: Filter chain integration
      - Apply date range filter + category filter + amount range filter
      - Verify filtered results match all criteria
    - Test: Chart data generation
      - Import transactions → Generate time series data → Verify chart data structure
    - Test: Dashboard metrics calculation
      - Import sample data → Calculate overview metrics
      - Verify totals, comparisons, and top categories are accurate
    - Maximum 10 tests to fill critical gaps only
  - [ ] 9.7 Run feature-specific test suite
    - Run ALL tests written for finance dashboard feature
    - Expected total: approximately 26-74 tests (16-64 from development + up to 10 integration)
    - Do NOT run tests for other features/modules
    - Generate test coverage report for finance module only
    - Verify all critical workflows pass
  - [ ] 9.8 Create test data loading script
    - Create `load_sample_data.py` script in src/finance/
    - Script should:
      - Load sample_categories.csv into finance_data/categories.csv
      - Load sample_label_rules.csv into finance_data/label_rules.csv
      - Optionally load sample_transactions.csv
      - Print confirmation messages
    - Add if __name__ == "__main__" section to run script
    - Add docstring explaining how to reset to sample data

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 26-74 tests total)
- No more than 10 additional tests added by testing-engineer
- Sample data files contain realistic, diverse transactions
- Sample categories form logical hierarchy with 2-3 nesting levels
- Sample rules demonstrate priority ordering and substring matching
- Integration tests cover critical end-to-end workflows
- Approval persistence is thoroughly tested (most critical feature)
- Import workflow is thoroughly tested (key entry point)
- Test data can be easily loaded for development and demos

---

### Phase 10: Documentation, Polish & Deployment

#### Task Group 10: Documentation & Final Polish
**Assigned implementer:** backend-engineer
**Dependencies:** Task Groups 1-9
**Complexity:** [Small]

- [ ] 10.0 Complete documentation and final polish
  - [ ] 10.1 Verify all files have if __name__ == "__main__" sections
    - Check finance_db.py has standalone usage example
    - Check finance_logic.py has standalone usage example
    - Check finance_analysis.py has standalone usage example
    - Check finance_workflow.py has standalone usage example
    - Check finance_app.py has server run command
    - Add missing sections if any
  - [ ] 10.2 Verify all functions have comprehensive docstrings
    - Review all functions in finance_db.py
    - Review all functions in finance_logic.py
    - Review all functions in finance_analysis.py
    - Review all functions in finance_workflow.py
    - Review all render functions in finance_app.py
    - Ensure docstrings explain: purpose, parameters, return values, business logic
    - Add examples where helpful
  - [ ] 10.3 Add inline comments for complex logic
    - Review category hierarchy parsing logic - add comments explaining tree traversal
    - Review substring matching logic - add comments explaining priority ordering
    - Review approval locking logic - add comments explaining why approved labels persist
    - Review category rollup logic - add comments explaining recursive aggregation
    - Review time-based grouping logic - add comments explaining period calculations
  - [ ] 10.4 Create comprehensive README for finance module
    - Section: Overview (what the finance dashboard does)
    - Section: Installation (pip install requirements)
    - Section: Quick Start (load sample data, run app, access in browser)
    - Section: User Guide
      - How to import CSV files (expected format)
      - How to create category hierarchy
      - How to define label rules
      - How to review and approve transactions
      - How to use dashboard visualizations
    - Section: Project Structure (explain each file's purpose)
    - Section: Architecture (explain layer separation: db, logic, analysis, workflow, app)
    - Section: Testing (how to run tests)
    - Section: Development (how to extend with new features)
    - Save to `src/finance/README.md`
  - [ ] 10.5 Create CSV format documentation
    - Document expected CSV import format:
      - Required columns: date, description, amount
      - Optional columns: account, category
      - Date format: YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY (auto-detect)
      - Amount format: negative for expenses, positive for income
    - Include examples from common banks (Chase, Bank of America, etc.)
    - Save to `src/finance/CSV_FORMAT.md`
  - [ ] 10.6 Optimize performance for large datasets
    - Profile app with 10,000+ transactions
    - Identify slow operations (likely: category rollup, large table rendering)
    - Add caching for expensive calculations (use functools.lru_cache)
    - Consider pagination for transaction tables (limit to 100 rows per page)
    - Add loading spinners for operations taking > 1 second
    - Test chart rendering performance with large datasets
  - [ ] 10.7 Final user acceptance testing
    - Test complete workflow with fresh sample data:
      - Load sample data script
      - Start app
      - Import sample transactions
      - Review auto-labeled transactions
      - Manually approve some, edit others
      - View dashboard charts
      - Apply filters
      - Verify all interactions work smoothly
    - Test error cases:
      - Upload malformed CSV (verify error message)
      - Try to delete category with dependencies (verify prevented)
      - Try to create duplicate category (verify error handling)
    - Test edge cases:
      - Empty transaction list
      - No approved transactions
      - All transactions approved
      - Category with no transactions
  - [ ] 10.8 Create deployment instructions
    - Document how to run in production mode (debug=False)
    - Document how to configure host and port
    - Document how to backup CSV data files
    - Consider deployment options: local, Heroku, Docker
    - Add to README.md deployment section

**Acceptance Criteria:**
- All files have if __name__ == "__main__" sections with examples
- All functions have comprehensive docstrings
- Complex logic has inline comments explaining business rules
- README provides complete user guide and developer documentation
- CSV format documentation helps users prepare their data
- App performs well with 10,000+ transactions
- Complete workflow can be executed without errors
- Error cases display helpful messages
- Deployment instructions are clear and complete
- Project follows Python Prototype Development Standards completely

---

## Execution Order Summary

**Recommended implementation sequence:**

1. **Phase 1** - Foundation & Database Layer (Task Group 1)
   - Establishes project structure and CSV data layer

2. **Phase 2** - Business Logic Layer (Task Group 2)
   - Implements core algorithms: category hierarchy, substring matching, approvals

3. **Phase 3** - Analysis & Aggregation Layer (Task Group 3)
   - Builds data analysis functions: grouping, rollups, comparisons

4. **Phase 4** - Workflow Orchestration Layer (Task Group 4)
   - Connects all layers with orchestration functions for each user action

5. **Phase 5** - Dash Application Foundation (Task Group 5)
   - Creates basic Dash app structure and reusable UI components

6. **Phase 6** - Data Management UIs (Task Group 6)
   - Implements Import Data, Manage Categories, and Manage Rules tabs

7. **Phase 7** - Dashboard & Review UIs (Task Group 7)
   - Implements Review Transactions, Overview, and Detailed Analysis tabs with basic charts

8. **Phase 8** - Advanced Visualizations (Task Group 8)
   - Adds stacked area chart, treemap, period comparison, and drill-down interactions

9. **Phase 9** - Integration Testing (Task Group 9)
   - Creates sample data and comprehensive integration tests

10. **Phase 10** - Documentation & Polish (Task Group 10)
    - Finalizes documentation, optimizes performance, validates user workflows

---

## Key Dependencies

- **Task Groups 2-4** depend on Task Group 1 (database layer must exist first)
- **Task Group 3** depends on Task Group 2 (analysis needs category hierarchy logic)
- **Task Group 4** depends on Task Groups 1-3 (workflow orchestrates all layers)
- **Task Groups 5-8** depend on Task Group 4 (UI needs workflow functions)
- **Task Group 6** depends on Task Group 5 (tabs need app foundation)
- **Task Group 7** depends on Task Group 6 (dashboard builds on data management)
- **Task Group 8** depends on Task Group 7 (advanced charts extend basic charts)
- **Task Group 9** depends on Task Groups 1-8 (integration tests require complete feature)
- **Task Group 10** depends on Task Groups 1-9 (documentation requires complete implementation)

---

## Testing Strategy Summary

- **Development Testing**: Each task group (1-8) writes 2-8 focused tests for critical functionality
- **Test Execution During Development**: Each task group runs ONLY its own tests, not the entire suite
- **Integration Testing**: Task Group 9 adds maximum 10 additional tests to fill critical gaps
- **Total Expected Tests**: Approximately 26-74 tests for the entire finance dashboard feature
- **Focus**: Test critical user workflows and integration points, not exhaustive coverage
- **Test Data**: Realistic sample data with 100+ transactions, 20+ categories, 15+ rules

---

## Special Considerations

1. **Plotly Dash vs Streamlit**: This project uses Plotly Dash, not Streamlit
   - Different callback model (@app.callback decorators)
   - Different component structure (dcc, html vs st)
   - State management via dcc.Store vs st.session_state

2. **Hierarchical Categories**: Novel feature requiring careful implementation
   - Arbitrary nesting depth (no hardcoded limits)
   - Parent-child relationship calculations
   - Category rollup aggregations (parent includes all children)
   - Validation to prevent orphaned categories

3. **Approval System**: Critical feature to prevent data loss
   - Approved labels must NEVER be overwritten automatically
   - Auto-labeling only applies to unapproved transactions
   - Re-importing same transactions preserves manual edits
   - This is the most important feature to test thoroughly

4. **Substring Matching Priority**: Business logic for conflict resolution
   - Rules sorted by priority (descending) before matching
   - First matching rule wins
   - Enables handling of ambiguous descriptions (e.g., "UBER EATS" vs "UBER")

5. **Time Grouping**: Flexible period-based aggregations
   - Support for day, week, month, quarter, year grouping
   - Handle fiscal vs calendar periods
   - Moving averages for trend analysis

6. **Performance**: Must handle 10,000+ transactions
   - Optimize category rollup calculations
   - Consider pagination for large tables
   - Cache expensive analysis results
   - Test with realistic data volumes

---

## Alignment with Standards

This tasks list is aligned with the following standards:

- **Python Prototype Development Standards** (CLAUDE.md):
  - Layer separation: _db.py, _logic.py, _analysis.py, _workflow.py, _app.py
  - Each file has `if __name__ == "__main__":` section
  - Comprehensive docstrings and inline comments
  - Standalone test sections for manual validation

- **Testing Standards** (test-writing.md):
  - Minimal tests during development (2-8 per task group)
  - Focus on core user flows and critical paths
  - Defer edge case testing to integration phase
  - Maximum 10 additional integration tests

- **General Conventions** (conventions.md):
  - Clear project structure
  - Comprehensive documentation (README, CSV format guide)
  - Environment configuration best practices
  - Dependency management

- **Tech Stack** (tech-stack.md):
  - Python with Plotly Dash framework
  - pandas for data manipulation
  - CSV for mock database
  - pytest for testing

This comprehensive tasks list provides a strategic, sequenced implementation plan for the finance dashboard project that can be executed efficiently by specialist implementers.
