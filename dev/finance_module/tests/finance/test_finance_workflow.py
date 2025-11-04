"""
test_finance_workflow.py - Integration tests for finance_workflow module

Tests complete workflows that orchestrate across database, logic, and analysis layers.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
import tempfile
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from finance import finance_workflow, finance_db


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def clean_database():
    """Clean database before and after each test."""
    # Setup: Clean database
    if finance_db.TRANSACTIONS_FILE.exists():
        finance_db.TRANSACTIONS_FILE.unlink()
    if finance_db.CATEGORIES_FILE.exists():
        finance_db.CATEGORIES_FILE.unlink()
    if finance_db.LABEL_RULES_FILE.exists():
        finance_db.LABEL_RULES_FILE.unlink()
    if finance_db.APPROVALS_FILE.exists():
        finance_db.APPROVALS_FILE.unlink()

    # Re-create empty files
    finance_db.ensure_data_dir_exists()
    pd.DataFrame(columns=['transaction_id', 'date', 'description', 'amount',
                         'account', 'original_category', 'import_date']).to_csv(
        finance_db.TRANSACTIONS_FILE, index=False)
    pd.DataFrame(columns=['category_id', 'category_path', 'parent_category',
                         'level', 'display_name', 'color']).to_csv(
        finance_db.CATEGORIES_FILE, index=False)
    pd.DataFrame(columns=['rule_id', 'substring', 'category_path',
                         'case_sensitive', 'priority', 'enabled']).to_csv(
        finance_db.LABEL_RULES_FILE, index=False)
    pd.DataFrame(columns=['transaction_id', 'approved_category',
                         'approval_date', 'approval_method']).to_csv(
        finance_db.APPROVALS_FILE, index=False)

    yield

    # Teardown (same as setup)


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file with sample transactions."""
    data = """date,description,amount,account
2025-01-15,STARBUCKS COFFEE,-5.50,Chase Credit
2025-01-16,UBER RIDE,-45.00,Chase Credit
2025-01-22,SHELL GAS STATION,-52.00,Chase Credit
2025-02-05,PAYCHECK DEPOSIT,3500.00,Chase Checking"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write(data)
        temp_path = f.name

    yield temp_path

    # Cleanup
    os.unlink(temp_path)


def setup_test_data():
    """Setup categories and label rules for testing."""
    # Add categories
    finance_db.add_category('cat_1', 'dining', '', 'Dining', '#FF0000')
    finance_db.add_category('cat_2', 'dining/coffee', 'dining', 'Coffee', '#FF5555')
    finance_db.add_category('cat_3', 'transportation', '', 'Transportation', '#0000FF')
    finance_db.add_category('cat_4', 'transportation/rideshare', 'transportation', 'Rideshare', '#5555FF')
    finance_db.add_category('cat_5', 'transportation/car', 'transportation', 'Car', '#8888FF')
    finance_db.add_category('cat_6', 'transportation/car/gas', 'transportation/car', 'Gas', '#AAAAFF')
    finance_db.add_category('cat_7', 'income', '', 'Income', '#00FF00')
    finance_db.add_category('cat_8', 'income/salary', 'income', 'Salary', '#55FF55')

    # Add label rules
    finance_db.add_label_rule('rule_1', 'starbucks', 'dining/coffee', False, 10, True)
    finance_db.add_label_rule('rule_2', 'coffee', 'dining/coffee', False, 5, True)
    finance_db.add_label_rule('rule_3', 'uber', 'transportation/rideshare', False, 15, True)
    finance_db.add_label_rule('rule_4', 'shell', 'transportation/car/gas', False, 10, True)
    finance_db.add_label_rule('rule_5', 'gas station', 'transportation/car/gas', False, 8, True)
    finance_db.add_label_rule('rule_6', 'paycheck', 'income/salary', False, 20, True)


# ============================================================================
# CSV IMPORT TESTS
# ============================================================================

def test_import_transactions_from_csv(clean_database, sample_csv_file):
    """Test importing transactions from CSV."""
    setup_test_data()

    result = finance_workflow.import_transactions_from_csv(
        sample_csv_file,
        auto_label=True
    )

    assert result['success'] is True
    assert result['imported_count'] == 4
    assert result['duplicate_count'] == 0
    assert result['labeled_count'] == 4  # All should match rules

    # Verify transactions were saved
    transactions = finance_db.load_transactions()
    assert len(transactions) == 4


def test_import_csv_with_duplicates(clean_database, sample_csv_file):
    """Test that duplicate transactions are detected."""
    setup_test_data()

    # First import
    result1 = finance_workflow.import_transactions_from_csv(sample_csv_file)
    assert result1['imported_count'] == 4

    # Second import (should detect duplicates)
    result2 = finance_workflow.import_transactions_from_csv(sample_csv_file)
    assert result2['duplicate_count'] == 4
    assert result2['imported_count'] == 0


def test_import_csv_missing_columns(clean_database):
    """Test error handling for invalid CSV."""
    # Create CSV with missing required columns
    data = "invalid,columns\n1,2"

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write(data)
        temp_path = f.name

    result = finance_workflow.import_transactions_from_csv(temp_path)

    assert result['success'] is False
    assert 'Missing required columns' in result['error']

    os.unlink(temp_path)


# ============================================================================
# LABEL APPLICATION TESTS
# ============================================================================

def test_apply_labels_to_all_transactions(clean_database, sample_csv_file):
    """Test applying labels to all transactions."""
    setup_test_data()

    # Import without auto-labeling
    finance_workflow.import_transactions_from_csv(sample_csv_file, auto_label=False)

    # Apply labels
    result = finance_workflow.apply_labels_to_all_transactions()

    assert result['success'] is True
    assert result['labeled_count'] == 4


def test_apply_labels_respects_approved(clean_database, sample_csv_file):
    """Test that approved labels are not overwritten."""
    setup_test_data()

    # Import and auto-label
    finance_workflow.import_transactions_from_csv(sample_csv_file, auto_label=True)

    # Get a transaction and approve it with different category
    transactions = finance_db.load_transactions()
    txn_id = transactions.iloc[0]['transaction_id']

    # Approve with a different category
    finance_workflow.approve_transaction_label(txn_id, 'income/salary', 'manual_edit')

    # Re-apply labels (should not overwrite approved)
    result = finance_workflow.apply_labels_to_all_transactions(overwrite_approved=False)

    # Check that approval still exists
    approval = finance_db.get_approval_for_transaction(txn_id)
    assert approval is not None
    assert approval['approved_category'] == 'income/salary'


def test_apply_labels_to_single_transaction(clean_database):
    """Test applying label to a single transaction."""
    setup_test_data()

    # Add a transaction
    finance_db.add_transaction('txn_1', '2025-01-15', 'STARBUCKS COFFEE', -5.50)

    # Apply label
    result = finance_workflow.apply_labels_to_transaction('txn_1')

    assert result['success'] is True
    assert result['category'] == 'dining/coffee'


# ============================================================================
# APPROVAL WORKFLOW TESTS
# ============================================================================

def test_approve_transaction_label(clean_database):
    """Test approving a transaction label."""
    setup_test_data()

    # Add a transaction
    finance_db.add_transaction('txn_1', '2025-01-15', 'COFFEE SHOP', -5.50)

    # Approve it
    result = finance_workflow.approve_transaction_label(
        'txn_1',
        'dining/coffee',
        'manual_accept'
    )

    assert result['success'] is True

    # Verify approval was saved
    approval = finance_db.get_approval_for_transaction('txn_1')
    assert approval is not None
    assert approval['approved_category'] == 'dining/coffee'


def test_approve_nonexistent_transaction(clean_database):
    """Test error handling when approving nonexistent transaction."""
    result = finance_workflow.approve_transaction_label(
        'nonexistent',
        'dining/coffee'
    )

    assert result['success'] is False
    assert 'not found' in result['error']


def test_approve_multiple_transactions(clean_database):
    """Test approving multiple transactions at once."""
    setup_test_data()

    # Add transactions
    finance_db.add_transaction('txn_1', '2025-01-15', 'COFFEE', -5.50)
    finance_db.add_transaction('txn_2', '2025-01-16', 'UBER', -20.00)

    # Approve multiple
    result = finance_workflow.approve_multiple_transactions(
        ['txn_1', 'txn_2'],
        ['dining/coffee', 'transportation/rideshare']
    )

    assert result['success'] is True
    assert result['approved_count'] == 2
    assert result['failed_count'] == 0


# ============================================================================
# DASHBOARD METRICS TESTS
# ============================================================================

def test_get_dashboard_overview(clean_database, sample_csv_file):
    """Test getting dashboard overview metrics."""
    setup_test_data()

    # Import transactions
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Get overview
    overview = finance_workflow.get_dashboard_overview()

    assert overview['success'] is True
    assert overview['total_transactions'] == 4
    assert overview['total_income'] == 3500.00
    assert abs(overview['total_expenses'] - (-102.50)) < 0.01


def test_get_dashboard_overview_with_date_filter(clean_database, sample_csv_file):
    """Test dashboard overview with date filtering."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Get January only
    overview = finance_workflow.get_dashboard_overview(
        start_date='2025-01-01',
        end_date='2025-01-31'
    )

    assert overview['success'] is True
    assert overview['total_transactions'] == 3  # Jan transactions only


def test_get_category_breakdown(clean_database, sample_csv_file):
    """Test getting category breakdown."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Get root categories
    breakdown = finance_workflow.get_category_breakdown(level=0)

    assert breakdown['success'] is True
    assert len(breakdown['categories']) > 0

    # Check that we have dining, transportation, and income
    category_names = [cat['name'] for cat in breakdown['categories']]
    assert 'Dining' in category_names
    assert 'Transportation' in category_names
    assert 'Income' in category_names


def test_get_time_series_data(clean_database, sample_csv_file):
    """Test getting time series data."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Get monthly series
    series = finance_workflow.get_time_series_data(period='month')

    assert series['success'] is True
    assert len(series['series']) == 2  # January and February


# ============================================================================
# FILTER AND AGGREGATE TESTS
# ============================================================================

def test_get_filtered_transactions(clean_database, sample_csv_file):
    """Test getting filtered transactions."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Filter by category
    result = finance_workflow.get_filtered_transactions(
        category='transportation'
    )

    assert result['success'] is True
    assert result['count'] == 2  # Uber + Gas


def test_get_filtered_transactions_multiple_filters(clean_database, sample_csv_file):
    """Test filtering with multiple criteria."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Filter by date and amount
    result = finance_workflow.get_filtered_transactions(
        date_start='2025-01-01',
        date_end='2025-01-31',
        amount_max=-10.0
    )

    assert result['success'] is True
    # Should get Uber (-45) and Gas (-52), not coffee (-5.50)
    assert result['count'] == 2


def test_get_filtered_transactions_by_text(clean_database, sample_csv_file):
    """Test filtering by description text."""
    setup_test_data()
    finance_workflow.import_transactions_from_csv(sample_csv_file)

    # Search for "gas"
    result = finance_workflow.get_filtered_transactions(search_text='gas')

    assert result['success'] is True
    assert result['count'] == 1


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Running finance_workflow integration tests ===\n")
    print("To run all tests with pytest:")
    print("  pytest tests/finance/test_finance_workflow.py -v\n")
    print("Running pytest now...")

    # Run pytest programmatically
    pytest.main([__file__, "-v"])
