"""
test_finance_logic.py - Unit tests for finance_logic module

Tests all business logic functions including hierarchy parsing, substring matching,
deduplication, and validation.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from finance import finance_logic


# ============================================================================
# CATEGORY HIERARCHY TESTS
# ============================================================================

def test_parse_category_path():
    """Test parsing category paths into components."""
    assert finance_logic.parse_category_path("transportation") == ["transportation"]
    assert finance_logic.parse_category_path("transportation/car") == ["transportation", "car"]
    assert finance_logic.parse_category_path("transportation/car/gas") == ["transportation", "car", "gas"]
    assert finance_logic.parse_category_path("") == []


def test_get_parent_category():
    """Test getting parent category from path."""
    assert finance_logic.get_parent_category("transportation/car/gas") == "transportation/car"
    assert finance_logic.get_parent_category("transportation/car") == "transportation"
    assert finance_logic.get_parent_category("transportation") == ""
    assert finance_logic.get_parent_category("") == ""


def test_get_category_level():
    """Test calculating category hierarchy level."""
    assert finance_logic.get_category_level("transportation") == 0
    assert finance_logic.get_category_level("transportation/car") == 1
    assert finance_logic.get_category_level("transportation/car/gas") == 2
    assert finance_logic.get_category_level("") == 0


def test_get_all_children():
    """Test getting direct children of a category."""
    # Create sample categories
    categories_data = [
        {'category_path': 'transportation', 'parent_category': ''},
        {'category_path': 'transportation/car', 'parent_category': 'transportation'},
        {'category_path': 'transportation/air_travel', 'parent_category': 'transportation'},
        {'category_path': 'transportation/car/gas', 'parent_category': 'transportation/car'},
        {'category_path': 'dining', 'parent_category': ''},
    ]
    categories_df = pd.DataFrame(categories_data)

    # Test getting children
    children = finance_logic.get_all_children("transportation", categories_df)
    assert len(children) == 2
    assert "transportation/car" in children
    assert "transportation/air_travel" in children

    # Test root has no children (in this dataset, root "" has children)
    children = finance_logic.get_all_children("dining", categories_df)
    assert len(children) == 0

    # Test category with one child
    children = finance_logic.get_all_children("transportation/car", categories_df)
    assert len(children) == 1
    assert "transportation/car/gas" in children


def test_get_all_descendants():
    """Test getting all descendants (recursive children)."""
    categories_data = [
        {'category_path': 'transportation', 'parent_category': ''},
        {'category_path': 'transportation/car', 'parent_category': 'transportation'},
        {'category_path': 'transportation/air_travel', 'parent_category': 'transportation'},
        {'category_path': 'transportation/car/gas', 'parent_category': 'transportation/car'},
        {'category_path': 'transportation/car/maintenance', 'parent_category': 'transportation/car'},
    ]
    categories_df = pd.DataFrame(categories_data)

    # Get all descendants of transportation
    descendants = finance_logic.get_all_descendants("transportation", categories_df)
    assert len(descendants) == 4  # car, air_travel, gas, maintenance
    assert "transportation/car" in descendants
    assert "transportation/air_travel" in descendants
    assert "transportation/car/gas" in descendants
    assert "transportation/car/maintenance" in descendants


def test_get_category_ancestors():
    """Test getting all ancestors of a category."""
    ancestors = finance_logic.get_category_ancestors("transportation/car/gas")
    assert ancestors == ["transportation/car", "transportation"]

    ancestors = finance_logic.get_category_ancestors("transportation/car")
    assert ancestors == ["transportation"]

    ancestors = finance_logic.get_category_ancestors("transportation")
    assert ancestors == []


def test_is_descendant_of():
    """Test checking if a category is descendant of another."""
    assert finance_logic.is_descendant_of("transportation/car/gas", "transportation") == True
    assert finance_logic.is_descendant_of("transportation/car/gas", "transportation/car") == True
    assert finance_logic.is_descendant_of("transportation/car", "transportation") == True
    assert finance_logic.is_descendant_of("dining/coffee", "transportation") == False
    assert finance_logic.is_descendant_of("transportation", "transportation") == False
    # Everything is descendant of empty string (root)
    assert finance_logic.is_descendant_of("transportation/car", "") == True


# ============================================================================
# SUBSTRING MATCHER TESTS
# ============================================================================

def test_match_transaction_to_category():
    """Test matching transaction description to category."""
    # Create sample rules
    rules_data = [
        {'rule_id': '1', 'substring': 'starbucks', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 10, 'enabled': True},
        {'rule_id': '2', 'substring': 'coffee', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 5, 'enabled': True},
        {'rule_id': '3', 'substring': 'uber', 'category_path': 'transportation/rideshare',
         'case_sensitive': False, 'priority': 15, 'enabled': True},
        {'rule_id': '4', 'substring': 'EXACT', 'category_path': 'test/exact',
         'case_sensitive': True, 'priority': 20, 'enabled': True},
    ]
    rules_df = pd.DataFrame(rules_data)

    # Test case-insensitive matching
    assert finance_logic.match_transaction_to_category("STARBUCKS #12345", rules_df) == "dining/coffee"
    assert finance_logic.match_transaction_to_category("uber trip", rules_df) == "transportation/rideshare"

    # Test priority ordering (starbucks has higher priority than coffee)
    # Both match, but starbucks (priority 10) should win over coffee (priority 5)
    assert finance_logic.match_transaction_to_category("Starbucks Coffee", rules_df) == "dining/coffee"

    # Test case-sensitive matching
    assert finance_logic.match_transaction_to_category("EXACT match", rules_df) == "test/exact"
    assert finance_logic.match_transaction_to_category("exact match", rules_df) == None

    # Test no match
    assert finance_logic.match_transaction_to_category("Grocery Store", rules_df) == None


def test_match_disabled_rules():
    """Test that disabled rules are not used for matching."""
    rules_data = [
        {'rule_id': '1', 'substring': 'test', 'category_path': 'category1',
         'case_sensitive': False, 'priority': 10, 'enabled': False},
    ]
    rules_df = pd.DataFrame(rules_data)

    # Should not match because rule is disabled
    assert finance_logic.match_transaction_to_category("test description", rules_df) == None


def test_batch_match_transactions():
    """Test matching multiple transactions at once."""
    transactions_data = [
        {'transaction_id': '1', 'description': 'STARBUCKS'},
        {'transaction_id': '2', 'description': 'UBER TRIP'},
        {'transaction_id': '3', 'description': 'UNKNOWN'},
    ]
    transactions_df = pd.DataFrame(transactions_data)

    rules_data = [
        {'rule_id': '1', 'substring': 'starbucks', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 10, 'enabled': True},
        {'rule_id': '2', 'substring': 'uber', 'category_path': 'transportation/rideshare',
         'case_sensitive': False, 'priority': 10, 'enabled': True},
    ]
    rules_df = pd.DataFrame(rules_data)

    matched_df = finance_logic.batch_match_transactions(transactions_df, rules_df)

    assert 'matched_category' in matched_df.columns
    assert matched_df.iloc[0]['matched_category'] == 'dining/coffee'
    assert matched_df.iloc[1]['matched_category'] == 'transportation/rideshare'
    assert pd.isna(matched_df.iloc[2]['matched_category'])


def test_get_unmatched_transactions():
    """Test filtering to only unmatched transactions."""
    transactions_data = [
        {'transaction_id': '1', 'description': 'STARBUCKS'},
        {'transaction_id': '2', 'description': 'UNKNOWN STORE'},
        {'transaction_id': '3', 'description': 'ANOTHER UNKNOWN'},
    ]
    transactions_df = pd.DataFrame(transactions_data)

    rules_data = [
        {'rule_id': '1', 'substring': 'starbucks', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 10, 'enabled': True},
    ]
    rules_df = pd.DataFrame(rules_data)

    unmatched = finance_logic.get_unmatched_transactions(transactions_df, rules_df)

    assert len(unmatched) == 2
    assert unmatched.iloc[0]['description'] == 'UNKNOWN STORE'
    assert unmatched.iloc[1]['description'] == 'ANOTHER UNKNOWN'


# ============================================================================
# DEDUPLICATION TESTS
# ============================================================================

def test_find_duplicate_transactions():
    """Test finding duplicate transactions."""
    existing_data = [
        {'transaction_id': '1', 'date': '2025-01-15', 'description': 'STARBUCKS', 'amount': -5.50},
        {'transaction_id': '2', 'date': '2025-01-16', 'description': 'UBER', 'amount': -20.00},
    ]
    existing_df = pd.DataFrame(existing_data)

    new_data = [
        {'transaction_id': '3', 'date': '2025-01-15', 'description': 'STARBUCKS', 'amount': -5.50},  # Duplicate
        {'transaction_id': '4', 'date': '2025-01-17', 'description': 'NEW STORE', 'amount': -10.00},  # Not duplicate
    ]
    new_df = pd.DataFrame(new_data)

    duplicates = finance_logic.find_duplicate_transactions(new_df, existing_df)

    assert len(duplicates) == 1
    assert duplicates.iloc[0]['description'] == 'STARBUCKS'


def test_find_duplicates_with_tolerance():
    """Test duplicate detection with date and amount tolerance."""
    existing_data = [
        {'transaction_id': '1', 'date': '2025-01-15', 'description': 'STORE', 'amount': -10.00},
    ]
    existing_df = pd.DataFrame(existing_data)

    new_data = [
        {'transaction_id': '2', 'date': '2025-01-16', 'description': 'STORE', 'amount': -10.05},
    ]
    new_df = pd.DataFrame(new_data)

    # Should not match with default tolerance (0 days, 0.01 amount)
    duplicates = finance_logic.find_duplicate_transactions(new_df, existing_df)
    assert len(duplicates) == 0

    # Should match with increased tolerance
    duplicates = finance_logic.find_duplicate_transactions(
        new_df, existing_df,
        date_tolerance_days=1,
        amount_tolerance=0.10
    )
    assert len(duplicates) == 1


def test_deduplicate_transactions():
    """Test removing duplicates from a DataFrame."""
    data = [
        {'transaction_id': '1', 'date': '2025-01-15', 'description': 'STARBUCKS', 'amount': -5.50},
        {'transaction_id': '1', 'date': '2025-01-15', 'description': 'STARBUCKS', 'amount': -5.50},  # Duplicate ID
        {'transaction_id': '2', 'date': '2025-01-15', 'description': 'STARBUCKS', 'amount': -5.50},  # Duplicate txn
        {'transaction_id': '3', 'date': '2025-01-16', 'description': 'UBER', 'amount': -20.00},
    ]
    df = pd.DataFrame(data)

    deduped = finance_logic.deduplicate_transactions(df)

    assert len(deduped) == 2  # Should keep only 2 unique transactions
    assert '1' in deduped['transaction_id'].values
    assert '3' in deduped['transaction_id'].values


def test_generate_transaction_id():
    """Test generating deterministic transaction IDs."""
    txn_id1 = finance_logic.generate_transaction_id("2025-01-15", "STARBUCKS COFFEE", -5.50)
    txn_id2 = finance_logic.generate_transaction_id("2025-01-15", "STARBUCKS COFFEE", -5.50)

    # Same inputs should generate same ID
    assert txn_id1 == txn_id2

    # Different inputs should generate different IDs
    txn_id3 = finance_logic.generate_transaction_id("2025-01-16", "STARBUCKS COFFEE", -5.50)
    assert txn_id1 != txn_id3


# ============================================================================
# VALIDATION TESTS
# ============================================================================

def test_is_valid_category_path():
    """Test category path validation."""
    # Valid paths
    assert finance_logic.is_valid_category_path("transportation") == True
    assert finance_logic.is_valid_category_path("transportation/car") == True
    assert finance_logic.is_valid_category_path("transportation/car/gas") == True
    assert finance_logic.is_valid_category_path("my_category") == True
    assert finance_logic.is_valid_category_path("my-category") == True
    assert finance_logic.is_valid_category_path("my category") == True

    # Invalid paths
    assert finance_logic.is_valid_category_path("") == False
    assert finance_logic.is_valid_category_path("/transportation") == False
    assert finance_logic.is_valid_category_path("transportation/") == False
    assert finance_logic.is_valid_category_path("transportation//car") == False


def test_validate_parent_exists():
    """Test validating that parent category exists."""
    categories_data = [
        {'category_path': 'transportation', 'parent_category': ''},
        {'category_path': 'transportation/car', 'parent_category': 'transportation'},
    ]
    categories_df = pd.DataFrame(categories_data)

    # Valid - parent exists
    valid, msg = finance_logic.validate_parent_exists("transportation/car/gas", categories_df)
    assert valid == True

    # Invalid - parent doesn't exist
    valid, msg = finance_logic.validate_parent_exists("nonexistent/child", categories_df)
    assert valid == False
    assert "does not exist" in msg

    # Valid - root category
    valid, msg = finance_logic.validate_parent_exists("new_root", categories_df)
    assert valid == True


def test_validate_no_circular_dependency():
    """Test circular dependency validation."""
    categories_data = [
        {'category_path': 'A', 'parent_category': ''},
        {'category_path': 'A/B', 'parent_category': 'A'},
    ]
    categories_df = pd.DataFrame(categories_data)

    # Valid - no circular dependency
    valid, msg = finance_logic.validate_no_circular_dependency("A/B/C", "A/B", categories_df)
    assert valid == True

    # Invalid - trying to make A child of A/B (circular)
    valid, msg = finance_logic.validate_no_circular_dependency("A", "A/B", categories_df)
    assert valid == False


def test_validate_category():
    """Test comprehensive category validation."""
    categories_data = [
        {'category_path': 'transportation', 'parent_category': ''},
        {'category_path': 'transportation/car', 'parent_category': 'transportation'},
    ]
    categories_df = pd.DataFrame(categories_data)

    # Valid category
    valid, msg = finance_logic.validate_category(
        "transportation/car/gas",
        "transportation/car",
        categories_df
    )
    assert valid == True

    # Invalid - parent doesn't exist
    valid, msg = finance_logic.validate_category(
        "nonexistent/child",
        "nonexistent",
        categories_df
    )
    assert valid == False

    # Invalid - parent mismatch
    valid, msg = finance_logic.validate_category(
        "transportation/car/gas",
        "transportation",  # Wrong parent (should be transportation/car)
        categories_df
    )
    assert valid == False


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Running finance_logic unit tests ===\n")
    print("To run all tests with pytest:")
    print("  pytest tests/finance/test_finance_logic.py -v\n")
    print("Running pytest now...")

    # Run pytest programmatically
    pytest.main([__file__, "-v"])
