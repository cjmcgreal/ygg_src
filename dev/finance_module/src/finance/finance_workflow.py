"""
finance_workflow.py - Workflow Orchestration Layer

Orchestrates between the UI and backend layers. Each function corresponds to a
user action and coordinates calls to the database, logic, and analysis layers.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Handle imports for both module and standalone execution
try:
    from finance import finance_db, finance_logic, finance_analysis
except ImportError:
    import finance_db
    import finance_logic
    import finance_analysis


# ============================================================================
# CSV IMPORT WORKFLOW
# ============================================================================

def import_transactions_from_csv(csv_file_path: str,
                                auto_label: bool = True) -> Dict[str, any]:
    """
    Import transactions from a CSV file.

    Workflow:
    1. Load and parse CSV file
    2. Generate transaction IDs if missing
    3. Check for duplicates against existing transactions
    4. Auto-label transactions using substring rules (if enabled)
    5. Save new transactions to database

    Args:
        csv_file_path (str): Path to CSV file to import
        auto_label (bool): Whether to apply auto-labeling (default: True)

    Returns:
        dict: Import results with statistics

    Example:
        >>> result = import_transactions_from_csv("data.csv")
        >>> print(f"Imported {result['imported_count']} transactions")
    """
    try:
        # Step 1: Load CSV (disable automatic date parsing to avoid confusion)
        new_transactions_df = pd.read_csv(csv_file_path, parse_dates=False)

        # Validate required columns
        required_columns = ['date', 'description', 'amount']
        missing_columns = [col for col in required_columns if col not in new_transactions_df.columns]
        if missing_columns:
            return {
                'success': False,
                'error': f"Missing required columns: {missing_columns}",
                'imported_count': 0,
                'duplicate_count': 0,
                'labeled_count': 0
            }

        # Ensure date column is string format
        new_transactions_df['date'] = new_transactions_df['date'].astype(str)

        # Ensure amount is numeric
        new_transactions_df['amount'] = pd.to_numeric(new_transactions_df['amount'], errors='coerce')

        # Step 2: Generate transaction IDs if missing
        if 'transaction_id' not in new_transactions_df.columns:
            new_transactions_df['transaction_id'] = new_transactions_df.apply(
                lambda row: finance_logic.generate_transaction_id(
                    row['date'], row['description'], row['amount']
                ), axis=1
            )

        # Add default values for optional columns
        if 'account' not in new_transactions_df.columns:
            new_transactions_df['account'] = ''
        if 'original_category' not in new_transactions_df.columns:
            new_transactions_df['original_category'] = ''
        if 'import_date' not in new_transactions_df.columns:
            new_transactions_df['import_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Step 3: Check for duplicates
        existing_transactions_df = finance_db.load_transactions()

        if not existing_transactions_df.empty:
            duplicates_df = finance_logic.find_duplicate_transactions(
                new_transactions_df, existing_transactions_df
            )
            duplicate_count = len(duplicates_df)

            # Remove duplicates from import
            if duplicate_count > 0:
                duplicate_ids = duplicates_df['transaction_id'].tolist()
                new_transactions_df = new_transactions_df[
                    ~new_transactions_df['transaction_id'].isin(duplicate_ids)
                ]
        else:
            duplicate_count = 0

        # Step 4: Auto-label transactions
        labeled_count = 0
        if auto_label and not new_transactions_df.empty:
            label_rules_df = finance_db.load_label_rules()
            if not label_rules_df.empty:
                new_transactions_df = finance_logic.batch_match_transactions(
                    new_transactions_df, label_rules_df
                )
                # Count how many were labeled
                labeled_count = new_transactions_df['matched_category'].notna().sum()

        # Step 5: Save to database
        imported_count = 0
        if not new_transactions_df.empty:
            # Add each transaction
            for _, txn in new_transactions_df.iterrows():
                success = finance_db.add_transaction(
                    transaction_id=txn['transaction_id'],
                    date=txn['date'],
                    description=txn['description'],
                    amount=txn['amount'],
                    account=txn.get('account', ''),
                    original_category=txn.get('original_category', '')
                )
                if success:
                    imported_count += 1

        return {
            'success': True,
            'imported_count': imported_count,
            'duplicate_count': duplicate_count,
            'labeled_count': labeled_count,
            'total_processed': len(new_transactions_df) + duplicate_count
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'imported_count': 0,
            'duplicate_count': 0,
            'labeled_count': 0
        }


# ============================================================================
# LABEL APPLICATION WORKFLOW
# ============================================================================

def apply_labels_to_all_transactions(overwrite_approved: bool = False) -> Dict[str, any]:
    """
    Apply substring matching rules to all transactions.

    Respects approved transaction labels unless overwrite_approved is True.

    Args:
        overwrite_approved (bool): Whether to overwrite approved labels (default: False)

    Returns:
        dict: Results with count of labeled transactions

    Example:
        >>> result = apply_labels_to_all_transactions()
        >>> print(f"Labeled {result['labeled_count']} transactions")
    """
    transactions_df = finance_db.load_transactions()
    label_rules_df = finance_db.load_label_rules()
    approvals_df = finance_db.load_approvals()

    if transactions_df.empty:
        return {
            'success': True,
            'labeled_count': 0,
            'message': 'No transactions to label'
        }

    if label_rules_df.empty:
        return {
            'success': True,
            'labeled_count': 0,
            'message': 'No label rules defined'
        }

    # Apply matching to all transactions
    matched_df = finance_logic.batch_match_transactions(
        transactions_df.copy(), label_rules_df
    )

    # If not overwriting approved, restore approved labels
    labeled_count = 0
    if not overwrite_approved and not approvals_df.empty:
        # Get approved transaction IDs
        approved_ids = approvals_df['transaction_id'].tolist()

        # For approved transactions, use approved category instead of matched
        for txn_id in approved_ids:
            if txn_id in matched_df['transaction_id'].values:
                approval = finance_db.get_approval_for_transaction(txn_id)
                if approval:
                    # Note: matched_category is only temporary for display
                    # We don't actually store it in transactions table
                    pass

        # Count non-approved transactions that got labeled
        non_approved_mask = ~matched_df['transaction_id'].isin(approved_ids)
        labeled_count = matched_df[non_approved_mask]['matched_category'].notna().sum()
    else:
        labeled_count = matched_df['matched_category'].notna().sum()

    return {
        'success': True,
        'labeled_count': labeled_count,
        'total_transactions': len(transactions_df)
    }


def apply_labels_to_transaction(transaction_id: str) -> Dict[str, any]:
    """
    Apply label rules to a single transaction.

    Args:
        transaction_id (str): Transaction ID to label

    Returns:
        dict: Result with matched category

    Example:
        >>> result = apply_labels_to_transaction("txn_001")
        >>> print(f"Matched category: {result['category']}")
    """
    # Get transaction
    txn = finance_db.get_transaction_by_id(transaction_id)
    if not txn:
        return {
            'success': False,
            'error': 'Transaction not found',
            'category': None
        }

    # Get label rules
    label_rules_df = finance_db.load_label_rules()
    if label_rules_df.empty:
        return {
            'success': True,
            'category': None,
            'message': 'No label rules defined'
        }

    # Match transaction
    category = finance_logic.match_transaction_to_category(
        txn['description'], label_rules_df
    )

    return {
        'success': True,
        'category': category
    }


# ============================================================================
# APPROVAL WORKFLOW
# ============================================================================

def approve_transaction_label(transaction_id: str,
                              category: str,
                              approval_method: str = 'manual_accept') -> Dict[str, any]:
    """
    Approve a transaction's category label.

    This locks the label so it won't be overwritten on future auto-labeling.

    Args:
        transaction_id (str): Transaction ID to approve
        category (str): Category to approve for this transaction
        approval_method (str): How approved (manual_accept, manual_edit, auto)

    Returns:
        dict: Result of approval

    Example:
        >>> result = approve_transaction_label("txn_001", "dining/coffee")
    """
    # Verify transaction exists
    txn = finance_db.get_transaction_by_id(transaction_id)
    if not txn:
        return {
            'success': False,
            'error': 'Transaction not found'
        }

    # Verify category exists
    categories_df = finance_db.load_categories()
    if not categories_df.empty:
        category_exists = category in categories_df['category_path'].values
        if not category_exists and category != '':  # Allow empty category
            return {
                'success': False,
                'error': f'Category "{category}" does not exist'
            }

    # Save approval
    success = finance_db.add_approval(transaction_id, category, approval_method)

    if success:
        return {
            'success': True,
            'message': f'Approved transaction {transaction_id} as "{category}"'
        }
    else:
        return {
            'success': False,
            'error': 'Failed to save approval'
        }


def approve_multiple_transactions(transaction_ids: List[str],
                                  categories: List[str]) -> Dict[str, any]:
    """
    Approve multiple transactions at once.

    Args:
        transaction_ids (List[str]): List of transaction IDs
        categories (List[str]): List of categories (same order as IDs)

    Returns:
        dict: Results with counts

    Example:
        >>> result = approve_multiple_transactions(
        >>>     ["txn_001", "txn_002"],
        >>>     ["dining/coffee", "transportation/car"]
        >>> )
    """
    if len(transaction_ids) != len(categories):
        return {
            'success': False,
            'error': 'transaction_ids and categories must have same length'
        }

    approved_count = 0
    failed_count = 0

    for txn_id, category in zip(transaction_ids, categories):
        result = approve_transaction_label(txn_id, category, 'manual_accept')
        if result['success']:
            approved_count += 1
        else:
            failed_count += 1

    return {
        'success': True,
        'approved_count': approved_count,
        'failed_count': failed_count
    }


# ============================================================================
# DASHBOARD METRICS WORKFLOW
# ============================================================================

def get_dashboard_overview(start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict[str, any]:
    """
    Get overview metrics for the dashboard.

    Args:
        start_date (str, optional): Filter start date (YYYY-MM-DD)
        end_date (str, optional): Filter end date (YYYY-MM-DD)

    Returns:
        dict: Dashboard metrics including totals, counts, and breakdowns

    Example:
        >>> metrics = get_dashboard_overview('2025-01-01', '2025-01-31')
        >>> print(f"Total spending: ${metrics['total_expenses']:.2f}")
    """
    # Load data
    transactions_df = finance_db.load_transactions()
    categories_df = finance_db.load_categories()
    label_rules_df = finance_db.load_label_rules()
    approvals_df = finance_db.load_approvals()

    if transactions_df.empty:
        return {
            'success': True,
            'total_transactions': 0,
            'total_income': 0.0,
            'total_expenses': 0.0,
            'net': 0.0,
            'labeled_count': 0,
            'approved_count': 0
        }

    # Apply date filter if specified
    if start_date or end_date:
        transactions_df = finance_analysis.filter_by_date_range(
            transactions_df, start_date, end_date
        )

    # Apply labels
    transactions_df = finance_logic.batch_match_transactions(
        transactions_df, label_rules_df
    )

    # Calculate summary statistics
    stats = finance_analysis.calculate_summary_statistics(transactions_df)

    # Count labeled and approved transactions
    labeled_count = transactions_df['matched_category'].notna().sum()
    approved_count = len(approvals_df)

    return {
        'success': True,
        'total_transactions': stats['count'],
        'total_income': stats['total_income'],
        'total_expenses': stats['total_expenses'],
        'net': stats['net'],
        'labeled_count': int(labeled_count),
        'approved_count': approved_count,
        'date_range': {
            'start': start_date,
            'end': end_date
        }
    }


def get_category_breakdown(start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          level: Optional[int] = None) -> Dict[str, any]:
    """
    Get spending breakdown by category with rollups.

    Args:
        start_date (str, optional): Filter start date
        end_date (str, optional): Filter end date
        level (int, optional): Filter to specific hierarchy level (0=root)

    Returns:
        dict: Category breakdown with amounts

    Example:
        >>> breakdown = get_category_breakdown(level=0)  # Root categories only
        >>> for cat in breakdown['categories']:
        >>>     print(f"{cat['name']}: ${cat['amount']:.2f}")
    """
    # Load data
    transactions_df = finance_db.load_transactions()
    categories_df = finance_db.load_categories()
    label_rules_df = finance_db.load_label_rules()

    if transactions_df.empty or categories_df.empty:
        return {
            'success': True,
            'categories': []
        }

    # Apply date filter
    if start_date or end_date:
        transactions_df = finance_analysis.filter_by_date_range(
            transactions_df, start_date, end_date
        )

    # Apply labels
    transactions_df = finance_logic.batch_match_transactions(
        transactions_df, label_rules_df
    )

    # Calculate rollups for all categories
    rollups_df = finance_analysis.calculate_all_category_rollups(
        transactions_df, categories_df
    )

    # Filter by level if specified
    if level is not None:
        rollups_df = rollups_df[rollups_df['level'] == level]

    # Convert to list of dicts
    categories = []
    for _, row in rollups_df.iterrows():
        categories.append({
            'path': row['category_path'],
            'name': row['display_name'],
            'amount': float(row['amount']),
            'level': int(row['level']),
            'color': row['color']
        })

    return {
        'success': True,
        'categories': categories
    }


def get_time_series_data(period: str = 'month',
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> Dict[str, any]:
    """
    Get time series data for plotting.

    Args:
        period (str): Grouping period (day, week, month, quarter, year)
        start_date (str, optional): Filter start date
        end_date (str, optional): Filter end date

    Returns:
        dict: Time series data

    Example:
        >>> data = get_time_series_data(period='month')
        >>> for point in data['series']:
        >>>     print(f"{point['date']}: ${point['amount']:.2f}")
    """
    # Load and filter transactions
    transactions_df = finance_db.load_transactions()

    if transactions_df.empty:
        return {
            'success': True,
            'series': [],
            'period': period
        }

    if start_date or end_date:
        transactions_df = finance_analysis.filter_by_date_range(
            transactions_df, start_date, end_date
        )

    # Group by period
    try:
        grouped_df = finance_analysis.group_by_period(transactions_df, period)
    except ValueError as e:
        return {
            'success': False,
            'error': str(e)
        }

    # Convert to list of dicts
    series = []
    for _, row in grouped_df.iterrows():
        # Get date column name (varies by period)
        date_col = [col for col in grouped_df.columns if col != 'amount'][0]
        date_val = row[date_col]

        # Convert to string
        if hasattr(date_val, 'strftime'):
            date_str = date_val.strftime('%Y-%m-%d')
        else:
            date_str = str(date_val)

        series.append({
            'date': date_str,
            'amount': float(row['amount'])
        })

    return {
        'success': True,
        'series': series,
        'period': period
    }


# ============================================================================
# FILTER AND AGGREGATE WORKFLOW
# ============================================================================

def get_filtered_transactions(date_start: Optional[str] = None,
                              date_end: Optional[str] = None,
                              category: Optional[str] = None,
                              amount_min: Optional[float] = None,
                              amount_max: Optional[float] = None,
                              search_text: Optional[str] = None) -> Dict[str, any]:
    """
    Get filtered and labeled transactions.

    Args:
        date_start (str, optional): Start date filter
        date_end (str, optional): End date filter
        category (str, optional): Category filter (includes descendants)
        amount_min (float, optional): Minimum amount
        amount_max (float, optional): Maximum amount
        search_text (str, optional): Text search in description

    Returns:
        dict: Filtered transactions

    Example:
        >>> result = get_filtered_transactions(
        >>>     category='transportation',
        >>>     date_start='2025-01-01'
        >>> )
        >>> print(f"Found {result['count']} transactions")
    """
    # Load data
    transactions_df = finance_db.load_transactions()
    categories_df = finance_db.load_categories()
    label_rules_df = finance_db.load_label_rules()
    approvals_df = finance_db.load_approvals()

    if transactions_df.empty:
        return {
            'success': True,
            'transactions': [],
            'count': 0
        }

    # Apply labels
    transactions_df = finance_logic.batch_match_transactions(
        transactions_df, label_rules_df
    )

    # Apply filters
    if date_start or date_end:
        transactions_df = finance_analysis.filter_by_date_range(
            transactions_df, date_start, date_end
        )

    if category:
        transactions_df = finance_analysis.filter_by_category(
            transactions_df, category, categories_df, include_descendants=True
        )

    if amount_min is not None or amount_max is not None:
        transactions_df = finance_analysis.filter_by_amount_range(
            transactions_df, amount_min, amount_max
        )

    if search_text:
        transactions_df = finance_analysis.filter_by_description(
            transactions_df, search_text, case_sensitive=False
        )

    # Add approval status
    if not approvals_df.empty:
        approved_ids = set(approvals_df['transaction_id'].tolist())
        transactions_df['is_approved'] = transactions_df['transaction_id'].isin(approved_ids)

        # Get approved categories
        approval_map = dict(zip(approvals_df['transaction_id'], approvals_df['approved_category']))
        transactions_df['approved_category'] = transactions_df['transaction_id'].map(approval_map)

        # Use approved category if available, else matched category
        transactions_df['display_category'] = transactions_df['approved_category'].fillna(
            transactions_df['matched_category']
        )
    else:
        transactions_df['is_approved'] = False
        transactions_df['approved_category'] = None
        transactions_df['display_category'] = transactions_df['matched_category']

    # Convert to list of dicts
    transactions = transactions_df.to_dict('records')

    return {
        'success': True,
        'transactions': transactions,
        'count': len(transactions)
    }


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Finance Workflow Module Test ===\n")

    # Note: These tests use the actual database files
    # Make sure to backup your data before running

    print("Test 1: Get dashboard overview...")
    overview = get_dashboard_overview()
    if overview['success']:
        print(f"  Total transactions: {overview['total_transactions']}")
        print(f"  Total income: ${overview['total_income']:.2f}")
        print(f"  Total expenses: ${overview['total_expenses']:.2f}")
        print(f"  Net: ${overview['net']:.2f}")

    print("\nTest 2: Get category breakdown...")
    breakdown = get_category_breakdown(level=0)
    if breakdown['success']:
        print(f"  Root categories: {len(breakdown['categories'])}")
        for cat in breakdown['categories'][:3]:
            print(f"    {cat['name']}: ${cat['amount']:.2f}")

    print("\nTest 3: Get time series data...")
    series = get_time_series_data(period='month')
    if series['success']:
        print(f"  Data points: {len(series['series'])}")
        for point in series['series'][:3]:
            print(f"    {point['date']}: ${point['amount']:.2f}")

    print("\nTest 4: Get filtered transactions...")
    filtered = get_filtered_transactions(amount_max=-10.0)
    if filtered['success']:
        print(f"  Transactions > $10: {filtered['count']}")

    print("\n=== All tests complete ===")
