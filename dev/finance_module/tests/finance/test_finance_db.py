"""
test_finance_db.py - Unit tests for finance_db module

Tests all CRUD operations for transactions, categories, label rules, and approvals.
"""

import pytest
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from finance import finance_db


@pytest.fixture
def clean_test_data():
    """
    Fixture to clean up test data before and after each test.
    Ensures tests run in isolation.
    """
    # Setup: Clear any existing test data
    if finance_db.TRANSACTIONS_FILE.exists():
        finance_db.TRANSACTIONS_FILE.unlink()
    if finance_db.CATEGORIES_FILE.exists():
        finance_db.CATEGORIES_FILE.unlink()
    if finance_db.LABEL_RULES_FILE.exists():
        finance_db.LABEL_RULES_FILE.unlink()
    if finance_db.APPROVALS_FILE.exists():
        finance_db.APPROVALS_FILE.unlink()

    # Re-create empty CSV files with headers
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

    # Teardown: Clean up after test
    # (same cleanup as setup)


# ============================================================================
# TRANSACTION TESTS
# ============================================================================

def test_load_transactions_empty(clean_test_data):
    """Test loading transactions when file is empty."""
    df = finance_db.load_transactions()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert 'transaction_id' in df.columns


def test_add_transaction(clean_test_data):
    """Test adding a new transaction."""
    success = finance_db.add_transaction(
        transaction_id="txn_001",
        date="2025-01-15",
        description="Coffee Shop",
        amount=-5.50,
        account="Chase"
    )
    assert success is True

    # Verify it was saved
    df = finance_db.load_transactions()
    assert len(df) == 1
    assert df.iloc[0]['transaction_id'] == "txn_001"
    assert df.iloc[0]['description'] == "Coffee Shop"
    assert df.iloc[0]['amount'] == -5.50


def test_add_duplicate_transaction(clean_test_data):
    """Test that adding duplicate transaction_id fails."""
    finance_db.add_transaction("txn_001", "2025-01-15", "First", -10.0)
    success = finance_db.add_transaction("txn_001", "2025-01-16", "Duplicate", -20.0)

    assert success is False

    # Verify only one transaction exists
    df = finance_db.load_transactions()
    assert len(df) == 1
    assert df.iloc[0]['description'] == "First"


def test_get_transaction_by_id(clean_test_data):
    """Test retrieving a transaction by ID."""
    finance_db.add_transaction("txn_001", "2025-01-15", "Coffee", -5.50)

    txn = finance_db.get_transaction_by_id("txn_001")
    assert txn is not None
    assert txn['transaction_id'] == "txn_001"
    assert txn['description'] == "Coffee"

    # Test non-existent ID
    txn = finance_db.get_transaction_by_id("nonexistent")
    assert txn is None


def test_delete_transaction(clean_test_data):
    """Test deleting a transaction."""
    finance_db.add_transaction("txn_001", "2025-01-15", "Coffee", -5.50)
    finance_db.add_transaction("txn_002", "2025-01-16", "Lunch", -12.00)

    # Delete one transaction
    success = finance_db.delete_transaction("txn_001")
    assert success is True

    df = finance_db.load_transactions()
    assert len(df) == 1
    assert df.iloc[0]['transaction_id'] == "txn_002"

    # Try to delete non-existent transaction
    success = finance_db.delete_transaction("nonexistent")
    assert success is False


# ============================================================================
# CATEGORY TESTS
# ============================================================================

def test_load_categories_empty(clean_test_data):
    """Test loading categories when file is empty."""
    df = finance_db.load_categories()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert 'category_path' in df.columns


def test_add_category(clean_test_data):
    """Test adding a new category."""
    success = finance_db.add_category(
        category_id="cat_001",
        category_path="dining/coffee",
        parent_category="dining",
        display_name="Coffee Shops",
        color="#FF5733"
    )
    assert success is True

    df = finance_db.load_categories()
    assert len(df) == 1
    assert df.iloc[0]['category_path'] == "dining/coffee"
    assert df.iloc[0]['level'] == 1  # dining is level 0, coffee is level 1


def test_add_root_category(clean_test_data):
    """Test adding a root-level category."""
    success = finance_db.add_category(
        category_id="cat_root",
        category_path="transportation",
        parent_category="",  # No parent = root
        display_name="Transportation"
    )
    assert success is True

    df = finance_db.load_categories()
    assert df.iloc[0]['level'] == 0
    assert df.iloc[0]['parent_category'] == ""


def test_category_level_calculation(clean_test_data):
    """Test that category levels are calculated correctly."""
    # Root level
    finance_db.add_category("cat_1", "transportation", "", "Transportation")

    # Level 1
    finance_db.add_category("cat_2", "transportation/car", "transportation", "Car")

    # Level 2
    finance_db.add_category("cat_3", "transportation/car/maintenance",
                           "transportation/car", "Maintenance")

    df = finance_db.load_categories()
    assert df[df['category_id'] == 'cat_1'].iloc[0]['level'] == 0
    assert df[df['category_id'] == 'cat_2'].iloc[0]['level'] == 1
    assert df[df['category_id'] == 'cat_3'].iloc[0]['level'] == 2


def test_get_category_by_path(clean_test_data):
    """Test retrieving a category by path."""
    finance_db.add_category("cat_001", "dining/coffee", "dining", "Coffee")

    cat = finance_db.get_category_by_path("dining/coffee")
    assert cat is not None
    assert cat['category_id'] == "cat_001"

    # Test non-existent path
    cat = finance_db.get_category_by_path("nonexistent/path")
    assert cat is None


# ============================================================================
# LABEL RULE TESTS
# ============================================================================

def test_load_label_rules_empty(clean_test_data):
    """Test loading label rules when file is empty."""
    df = finance_db.load_label_rules()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert 'substring' in df.columns


def test_add_label_rule(clean_test_data):
    """Test adding a new label rule."""
    success = finance_db.add_label_rule(
        rule_id="rule_001",
        substring="starbucks",
        category_path="dining/coffee",
        case_sensitive=False,
        priority=10,
        enabled=True
    )
    assert success is True

    df = finance_db.load_label_rules()
    assert len(df) == 1
    assert df.iloc[0]['substring'] == "starbucks"
    assert df.iloc[0]['priority'] == 10
    assert df.iloc[0]['enabled'] == True


def test_label_rule_priorities(clean_test_data):
    """Test that label rules maintain priority ordering."""
    finance_db.add_label_rule("rule_1", "coffee", "dining/coffee", priority=5)
    finance_db.add_label_rule("rule_2", "uber", "transportation/rideshare", priority=20)
    finance_db.add_label_rule("rule_3", "gas", "transportation/car/gas", priority=10)

    df = finance_db.load_label_rules()
    df_sorted = df.sort_values('priority', ascending=False)

    # Should be sorted: uber (20), gas (10), coffee (5)
    assert df_sorted.iloc[0]['substring'] == "uber"
    assert df_sorted.iloc[1]['substring'] == "gas"
    assert df_sorted.iloc[2]['substring'] == "coffee"


# ============================================================================
# APPROVAL TESTS
# ============================================================================

def test_load_approvals_empty(clean_test_data):
    """Test loading approvals when file is empty."""
    df = finance_db.load_approvals()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert 'transaction_id' in df.columns


def test_add_approval(clean_test_data):
    """Test adding a new approval."""
    success = finance_db.add_approval(
        transaction_id="txn_001",
        approved_category="dining/coffee",
        approval_method="manual_accept"
    )
    assert success is True

    df = finance_db.load_approvals()
    assert len(df) == 1
    assert df.iloc[0]['transaction_id'] == "txn_001"
    assert df.iloc[0]['approved_category'] == "dining/coffee"


def test_update_existing_approval(clean_test_data):
    """Test that adding approval for existing transaction updates it."""
    # First approval
    finance_db.add_approval("txn_001", "dining/coffee", "manual_accept")

    # Update approval
    finance_db.add_approval("txn_001", "dining/restaurants", "manual_edit")

    df = finance_db.load_approvals()
    assert len(df) == 1  # Should still be only one record
    assert df.iloc[0]['approved_category'] == "dining/restaurants"
    assert df.iloc[0]['approval_method'] == "manual_edit"


def test_is_transaction_approved(clean_test_data):
    """Test checking if transaction is approved."""
    # Not approved initially
    assert finance_db.is_transaction_approved("txn_001") is False

    # Add approval
    finance_db.add_approval("txn_001", "dining/coffee")

    # Now should be approved
    assert finance_db.is_transaction_approved("txn_001") is True


def test_get_approval_for_transaction(clean_test_data):
    """Test retrieving approval details for a transaction."""
    finance_db.add_approval("txn_001", "dining/coffee", "manual_accept")

    approval = finance_db.get_approval_for_transaction("txn_001")
    assert approval is not None
    assert approval['approved_category'] == "dining/coffee"
    assert approval['approval_method'] == "manual_accept"

    # Test non-existent approval
    approval = finance_db.get_approval_for_transaction("nonexistent")
    assert approval is None


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Running finance_db unit tests ===\n")
    print("To run all tests with pytest:")
    print("  pytest tests/finance/test_finance_db.py -v\n")
    print("To run a specific test:")
    print("  pytest tests/finance/test_finance_db.py::test_add_transaction -v\n")
    print("Running pytest now...")

    # Run pytest programmatically
    pytest.main([__file__, "-v"])
