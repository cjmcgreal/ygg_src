"""
finance_app.py - Main Dash Application

Main Plotly Dash application for the finance dashboard.
Provides tabbed interface for importing data, managing categories,
reviewing transactions, and viewing analytics.
"""

import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import base64
import io

# Handle imports for both module and standalone execution
import sys
from pathlib import Path

# Add src to path if running standalone
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from finance import finance_workflow, finance_db
except ImportError:
    # Try direct import for standalone execution
    try:
        import finance_workflow
        import finance_db
    except ImportError:
        # Add current directory to path
        sys.path.insert(0, str(Path(__file__).parent))
        import finance_workflow
        import finance_db


# ============================================================================
# APP INITIALIZATION
# ============================================================================

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Finance Dashboard"


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_navbar():
    """Create navigation bar."""
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("GitHub", href="https://github.com")),
        ],
        brand="Finance Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        className="mb-4"
    )
    return navbar


def create_overview_tab():
    """Create the Overview/Dashboard tab layout."""
    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Dashboard Overview", className="mb-4"),
            ])
        ]),

        # Metrics Cards Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Total Income", className="card-title"),
                        html.H3(id="metric-total-income", children="$0.00", className="text-success"),
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Total Expenses", className="card-title"),
                        html.H3(id="metric-total-expenses", children="$0.00", className="text-danger"),
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Net", className="card-title"),
                        html.H3(id="metric-net", children="$0.00", className="text-info"),
                    ])
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Transactions", className="card-title"),
                        html.H3(id="metric-total-transactions", children="0"),
                    ])
                ])
            ], width=3),
        ], className="mb-4"),

        # Date Range Filter
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Label("Date Range:"),
                        dcc.DatePickerRange(
                            id='overview-date-range',
                            start_date=(datetime.now() - timedelta(days=30)).date(),
                            end_date=datetime.now().date(),
                            display_format='YYYY-MM-DD'
                        ),
                        dbc.Button("Refresh", id="overview-refresh-btn", color="primary", className="ms-2"),
                    ])
                ])
            ])
        ], className="mb-4"),

        # Charts Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Spending Over Time", className="card-title"),
                        dcc.Graph(id="overview-time-series")
                    ])
                ])
            ], width=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Category Breakdown", className="card-title"),
                        dcc.Graph(id="overview-category-pie")
                    ])
                ])
            ], width=4),
        ]),
    ], fluid=True)

    return layout


def create_import_tab():
    """Create the Import Data tab layout."""
    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Import Transactions", className="mb-4"),
            ])
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Upload CSV File"),
                        html.P("Upload a CSV file with columns: date, description, amount, account (optional)"),
                        dcc.Upload(
                            id='upload-csv',
                            children=dbc.Button("Select CSV File", color="primary"),
                            multiple=False
                        ),
                        html.Div(id='upload-status', className="mt-3"),
                        html.Hr(),
                        dbc.Checkbox(
                            id='auto-label-checkbox',
                            label='Auto-label transactions using rules',
                            value=True,
                            className="mb-3"
                        ),
                        dbc.Button("Import Transactions", id="import-btn", color="success", disabled=True),
                    ])
                ])
            ], width=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Import Results"),
                        html.Div(id='import-results'),
                    ])
                ])
            ], width=6),
        ]),

        html.Hr(className="my-4"),

        # Recent Imports History
        dbc.Row([
            dbc.Col([
                html.H5("Current Transactions"),
                html.Div(id='transactions-summary'),
            ])
        ]),
    ], fluid=True)

    return layout


def create_categories_tab():
    """Create the Manage Categories tab layout."""
    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Manage Categories", className="mb-4"),
            ])
        ]),

        dbc.Row([
            # Categories List
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Category Hierarchy"),
                        html.Div(id='categories-list'),
                        dbc.Button("Refresh", id="categories-refresh-btn", color="secondary", className="mt-3"),
                    ])
                ])
            ], width=6),

            # Add New Category
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Add New Category"),
                        dbc.Label("Category Path (e.g., transportation/car)"),
                        dbc.Input(id='new-category-path', type='text', placeholder='category/subcategory'),
                        dbc.Label("Display Name", className="mt-2"),
                        dbc.Input(id='new-category-name', type='text', placeholder='Display Name'),
                        dbc.Label("Color", className="mt-2"),
                        dbc.Input(id='new-category-color', type='color', value='#3498db'),
                        dbc.Button("Add Category", id="add-category-btn", color="primary", className="mt-3"),
                        html.Div(id='add-category-status', className="mt-3"),
                    ])
                ])
            ], width=6),
        ], className="mb-4"),

        html.Hr(),

        # Label Rules Section
        dbc.Row([
            dbc.Col([
                html.H5("Label Rules"),
                html.P("Define substring patterns to automatically categorize transactions"),
            ])
        ]),

        dbc.Row([
            # Rules List
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Current Rules"),
                        html.Div(id='rules-list'),
                        dbc.Button("Refresh Rules", id="rules-refresh-btn", color="secondary", className="mt-3"),
                    ])
                ])
            ], width=6),

            # Add New Rule
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Add New Rule"),
                        dbc.Label("Substring to Match"),
                        dbc.Input(id='new-rule-substring', type='text', placeholder='starbucks'),
                        dbc.Label("Category Path", className="mt-2"),
                        dbc.Input(id='new-rule-category', type='text', placeholder='dining/coffee'),
                        dbc.Label("Priority (higher = checked first)", className="mt-2"),
                        dbc.Input(id='new-rule-priority', type='number', value=10),
                        dbc.Checkbox(
                            id='new-rule-case-sensitive',
                            label='Case Sensitive',
                            value=False,
                            className="mt-2"
                        ),
                        dbc.Button("Add Rule", id="add-rule-btn", color="primary", className="mt-3"),
                        html.Div(id='add-rule-status', className="mt-3"),
                    ])
                ])
            ], width=6),
        ]),
    ], fluid=True)

    return layout


def create_transactions_tab():
    """Create the Review Transactions tab layout."""
    layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H3("Review Transactions", className="mb-4"),
            ])
        ]),

        # Filters
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Filters"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Date Range"),
                                dcc.DatePickerRange(
                                    id='transactions-date-range',
                                    display_format='YYYY-MM-DD'
                                ),
                            ], width=4),
                            dbc.Col([
                                dbc.Label("Category"),
                                dcc.Dropdown(id='transactions-category-filter', placeholder='All Categories'),
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Search"),
                                dbc.Input(id='transactions-search', type='text', placeholder='Search description'),
                            ], width=3),
                            dbc.Col([
                                dbc.Button("Apply Filters", id="transactions-filter-btn", color="primary", className="mt-4"),
                            ], width=2),
                        ]),
                    ])
                ])
            ])
        ], className="mb-4"),

        # Transactions Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("Transactions"),
                        html.Div(id='transactions-table-container'),
                        html.Div(id='transactions-status', className="mt-3"),
                    ])
                ])
            ])
        ]),

        # Action Buttons
        dbc.Row([
            dbc.Col([
                dbc.Button("Apply Labels to All", id="apply-labels-btn", color="info", className="mt-3 me-2"),
                dbc.Button("Refresh", id="transactions-refresh-btn", color="secondary", className="mt-3"),
            ])
        ]),
    ], fluid=True)

    return layout


# ============================================================================
# MAIN LAYOUT
# ============================================================================

app.layout = dbc.Container([
    create_navbar(),

    dcc.Store(id='uploaded-file-data'),  # Store for uploaded file

    dbc.Tabs([
        dbc.Tab(create_overview_tab(), label="📊 Overview", tab_id="overview"),
        dbc.Tab(create_import_tab(), label="📥 Import Data", tab_id="import"),
        dbc.Tab(create_categories_tab(), label="🏷️ Manage Categories", tab_id="categories"),
        dbc.Tab(create_transactions_tab(), label="💳 Review Transactions", tab_id="transactions"),
    ], id="main-tabs", active_tab="overview"),

], fluid=True, className="p-4")


# ============================================================================
# CALLBACKS - OVERVIEW TAB
# ============================================================================

@callback(
    [Output('metric-total-income', 'children'),
     Output('metric-total-expenses', 'children'),
     Output('metric-net', 'children'),
     Output('metric-total-transactions', 'children'),
     Output('overview-time-series', 'figure'),
     Output('overview-category-pie', 'figure')],
    [Input('overview-refresh-btn', 'n_clicks')],
    [State('overview-date-range', 'start_date'),
     State('overview-date-range', 'end_date')]
)
def update_overview(n_clicks, start_date, end_date):
    """Update overview dashboard metrics and charts."""
    # Get overview data
    overview = finance_workflow.get_dashboard_overview(start_date, end_date)

    if not overview['success']:
        return "$0.00", "$0.00", "$0.00", "0", {}, {}

    # Format metrics
    income = f"${overview['total_income']:,.2f}"
    expenses = f"${abs(overview['total_expenses']):,.2f}"
    net = f"${overview['net']:,.2f}"
    transactions = str(overview['total_transactions'])

    # Get time series data
    time_series_data = finance_workflow.get_time_series_data('month', start_date, end_date)

    # Create time series chart
    if time_series_data['success'] and time_series_data['series']:
        df = pd.DataFrame(time_series_data['series'])
        fig_time = px.line(df, x='date', y='amount', title='Spending Over Time')
        fig_time.update_layout(xaxis_title='Date', yaxis_title='Amount ($)')
    else:
        fig_time = go.Figure()
        fig_time.update_layout(title='No Data Available')

    # Get category breakdown
    breakdown = finance_workflow.get_category_breakdown(start_date, end_date, level=0)

    # Create category pie chart
    if breakdown['success'] and breakdown['categories']:
        df_cat = pd.DataFrame(breakdown['categories'])
        # Filter to expenses only (negative amounts)
        df_expenses = df_cat[df_cat['amount'] < 0].copy()
        df_expenses['amount'] = abs(df_expenses['amount'])

        if not df_expenses.empty:
            fig_pie = px.pie(df_expenses, values='amount', names='name',
                            title='Spending by Category',
                            color_discrete_sequence=df_expenses['color'].tolist())
        else:
            fig_pie = go.Figure()
            fig_pie.update_layout(title='No Expense Data')
    else:
        fig_pie = go.Figure()
        fig_pie.update_layout(title='No Categories')

    return income, expenses, net, transactions, fig_time, fig_pie


# ============================================================================
# CALLBACKS - IMPORT TAB
# ============================================================================

@callback(
    [Output('uploaded-file-data', 'data'),
     Output('upload-status', 'children'),
     Output('import-btn', 'disabled')],
    [Input('upload-csv', 'contents')],
    [State('upload-csv', 'filename')]
)
def handle_file_upload(contents, filename):
    """Handle CSV file upload."""
    if contents is None:
        return None, "", True

    # Parse uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        # Save to temporary location
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as f:
            f.write(decoded)
            temp_path = f.name

        status = dbc.Alert(f"✓ File '{filename}' uploaded successfully. Click Import to proceed.", color="success")
        return temp_path, status, False

    except Exception as e:
        status = dbc.Alert(f"✗ Error uploading file: {str(e)}", color="danger")
        return None, status, True


@callback(
    [Output('import-results', 'children'),
     Output('transactions-summary', 'children')],
    [Input('import-btn', 'n_clicks')],
    [State('uploaded-file-data', 'data'),
     State('auto-label-checkbox', 'value')]
)
def import_transactions(n_clicks, file_path, auto_label):
    """Import transactions from uploaded CSV."""
    if n_clicks is None or file_path is None:
        # Show current summary
        transactions = finance_db.load_transactions()
        summary = html.Div([
            html.P(f"Total transactions in database: {len(transactions)}"),
        ])
        return html.Div(), summary

    # Import transactions
    result = finance_workflow.import_transactions_from_csv(file_path, auto_label=auto_label)

    if result['success']:
        results_display = dbc.Alert([
            html.H5("✓ Import Successful", className="alert-heading"),
            html.P(f"Imported: {result['imported_count']} transactions"),
            html.P(f"Duplicates skipped: {result['duplicate_count']}"),
            html.P(f"Auto-labeled: {result['labeled_count']}"),
        ], color="success")
    else:
        results_display = dbc.Alert([
            html.H5("✗ Import Failed", className="alert-heading"),
            html.P(f"Error: {result['error']}"),
        ], color="danger")

    # Update summary
    transactions = finance_db.load_transactions()
    summary = html.Div([
        html.P(f"Total transactions in database: {len(transactions)}"),
    ])

    return results_display, summary


# ============================================================================
# CALLBACKS - CATEGORIES TAB
# ============================================================================

@callback(
    Output('categories-list', 'children'),
    [Input('categories-refresh-btn', 'n_clicks')]
)
def display_categories(n_clicks):
    """Display category hierarchy."""
    categories_df = finance_db.load_categories()

    if categories_df.empty:
        return html.P("No categories defined. Add your first category below!", className="text-muted")

    # Sort by level then by path
    categories_df = categories_df.sort_values(['level', 'category_path'])

    # Build hierarchical display
    items = []
    for _, cat in categories_df.iterrows():
        level = int(cat['level'])
        indent = "  " * level  # Indent based on level

        # Create colored badge for category
        badge = dbc.Badge(
            cat['display_name'],
            color="light",
            className="me-2",
            style={'backgroundColor': cat['color'], 'color': 'white'}
        )

        # Display with indentation
        item = html.Div([
            html.Span(indent, style={'white-space': 'pre'}),
            badge,
            html.Code(cat['category_path'], className="text-muted ms-2")
        ], className="mb-1")

        items.append(item)

    return html.Div(items, style={'fontFamily': 'monospace'})


@callback(
    Output('add-category-status', 'children'),
    [Input('add-category-btn', 'n_clicks')],
    [State('new-category-path', 'value'),
     State('new-category-name', 'value'),
     State('new-category-color', 'value')]
)
def add_new_category(n_clicks, path, name, color):
    """Add a new category."""
    if n_clicks is None:
        return html.Div()

    if not path:
        return dbc.Alert("Please enter a category path", color="warning")

    # Validate path format
    from finance import finance_logic
    if not finance_logic.is_valid_category_path(path):
        return dbc.Alert(f"Invalid category path: '{path}'. Use format like 'category/subcategory'", color="danger")

    # Get parent and validate
    parent = finance_logic.get_parent_category(path)
    categories_df = finance_db.load_categories()

    valid, msg = finance_logic.validate_category(path, parent, categories_df)
    if not valid:
        return dbc.Alert(f"Validation error: {msg}", color="danger")

    # Generate ID
    category_id = f"cat_{len(categories_df) + 1}"

    # Use path as name if not provided
    if not name:
        name = path.split('/')[-1].replace('_', ' ').title()

    # Add category
    success = finance_db.add_category(
        category_id=category_id,
        category_path=path,
        parent_category=parent,
        display_name=name,
        color=color or '#3498db'
    )

    if success:
        return dbc.Alert(f"✓ Category '{path}' added successfully!", color="success")
    else:
        return dbc.Alert(f"✗ Category '{path}' already exists", color="danger")


@callback(
    Output('rules-list', 'children'),
    [Input('rules-refresh-btn', 'n_clicks')]
)
def display_label_rules(n_clicks):
    """Display label rules."""
    rules_df = finance_db.load_label_rules()

    if rules_df.empty:
        return html.P("No label rules defined. Add your first rule below!", className="text-muted")

    # Sort by priority (highest first)
    rules_df = rules_df.sort_values('priority', ascending=False)

    # Build table
    rows = []
    for _, rule in rules_df.iterrows():
        row = html.Tr([
            html.Td(rule['substring'], style={'fontFamily': 'monospace'}),
            html.Td(rule['category_path']),
            html.Td(str(rule['priority']), className="text-center"),
            html.Td("✓" if rule['enabled'] else "✗", className="text-center"),
        ])
        rows.append(row)

    table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Substring"),
            html.Th("Category"),
            html.Th("Priority"),
            html.Th("Enabled"),
        ])),
        html.Tbody(rows)
    ], bordered=True, hover=True, size='sm')

    return table


@callback(
    Output('add-rule-status', 'children'),
    [Input('add-rule-btn', 'n_clicks')],
    [State('new-rule-substring', 'value'),
     State('new-rule-category', 'value'),
     State('new-rule-priority', 'value'),
     State('new-rule-case-sensitive', 'value')]
)
def add_new_rule(n_clicks, substring, category, priority, case_sensitive):
    """Add a new label rule."""
    if n_clicks is None:
        return html.Div()

    if not substring or not category:
        return dbc.Alert("Please enter both substring and category", color="warning")

    # Validate category exists
    categories_df = finance_db.load_categories()
    if not categories_df.empty and category not in categories_df['category_path'].values:
        return dbc.Alert(f"Category '{category}' does not exist. Create it first.", color="danger")

    # Generate rule ID
    rules_df = finance_db.load_label_rules()
    rule_id = f"rule_{len(rules_df) + 1}"

    # Add rule
    success = finance_db.add_label_rule(
        rule_id=rule_id,
        substring=substring,
        category_path=category,
        case_sensitive=case_sensitive or False,
        priority=priority or 10,
        enabled=True
    )

    if success:
        return dbc.Alert(f"✓ Rule '{substring}' → '{category}' added successfully!", color="success")
    else:
        return dbc.Alert(f"✗ Rule already exists", color="danger")


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
