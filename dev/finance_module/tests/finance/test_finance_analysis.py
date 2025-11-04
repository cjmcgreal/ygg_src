"""
test_finance_analysis.py - Unit tests for finance_analysis module

Tests all analysis functions including time grouping, category rollups,
comparisons, and statistics.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from finance import finance_analysis


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def sample_transactions():
    """Sample transactions for testing."""
    data = [
        {'transaction_id': '1', 'date': '2025-01-15', 'description': 'COFFEE', 'amount': -5.50, 'matched_category': 'dining/coffee'},
        {'transaction_id': '2', 'date': '2025-01-16', 'description': 'UBER', 'amount': -45.00, 'matched_category': 'transportation/rideshare'},
        {'transaction_id': '3', 'date': '2025-01-22', 'description': 'GAS', 'amount': -52.00, 'matched_category': 'transportation/car/gas'},
        {'transaction_id': '4', 'date': '2025-01-30', 'description': 'RESTAURANT', 'amount': -85.25, 'matched_category': 'dining/restaurants'},
        {'transaction_id': '5', 'date': '2025-02-05', 'description': 'COFFEE', 'amount': -6.75, 'matched_category': 'dining/coffee'},
        {'transaction_id': '6', 'date': '2025-02-10', 'description': 'PAYCHECK', 'amount': 3500.00, 'matched_category': 'income/salary'},
        {'transaction_id': '7', 'date': '2025-02-15', 'description': 'GAS', 'amount': -48.00, 'matched_category': 'transportation/car/gas'},
    ]
    return pd.DataFrame(data)


@pytest.fixture
def sample_categories():
    """Sample categories with hierarchy."""
    data = [
        {'category_path': 'dining', 'parent_category': '', 'level': 0, 'display_name': 'Dining', 'color': '#FF0000'},
        {'category_path': 'dining/coffee', 'parent_category': 'dining', 'level': 1, 'display_name': 'Coffee', 'color': '#FF5555'},
        {'category_path': 'dining/restaurants', 'parent_category': 'dining', 'level': 1, 'display_name': 'Restaurants', 'color': '#FFAAAA'},
        {'category_path': 'transportation', 'parent_category': '', 'level': 0, 'display_name': 'Transportation', 'color': '#0000FF'},
        {'category_path': 'transportation/car', 'parent_category': 'transportation', 'level': 1, 'display_name': 'Car', 'color': '#5555FF'},
        {'category_path': 'transportation/car/gas', 'parent_category': 'transportation/car', 'level': 2, 'display_name': 'Gas', 'color': '#AAAAFF'},
        {'category_path': 'transportation/rideshare', 'parent_category': 'transportation', 'level': 1, 'display_name': 'Rideshare', 'color': '#8888FF'},
        {'category_path': 'income', 'parent_category': '', 'level': 0, 'display_name': 'Income', 'color': '#00FF00'},
        {'category_path': 'income/salary', 'parent_category': 'income', 'level': 1, 'display_name': 'Salary', 'color': '#55FF55'},
    ]
    return pd.DataFrame(data)


# ============================================================================
# TIME GROUPING TESTS
# ============================================================================

def test_group_by_day(sample_transactions):
    """Test grouping by day."""
    result = finance_analysis.group_by_day(sample_transactions)

    assert len(result) == 7  # 7 unique dates
    assert 'date' in result.columns
    assert 'amount' in result.columns

    # Check that dates are sorted
    dates = result['date'].tolist()
    assert dates == sorted(dates)


def test_group_by_week(sample_transactions):
    """Test grouping by week."""
    result = finance_analysis.group_by_week(sample_transactions)

    assert 'week_start' in result.columns
    assert 'amount' in result.columns
    assert len(result) > 0


def test_group_by_month(sample_transactions):
    """Test grouping by month."""
    result = finance_analysis.group_by_month(sample_transactions)

    assert 'month_start' in result.columns
    assert 'amount' in result.columns
    assert len(result) == 2  # January and February

    # Check January total
    jan_row = result[result['month_start'] == '2025-01-01']
    assert len(jan_row) == 1
    jan_total = jan_row.iloc[0]['amount']
    # -5.50 + -45.00 + -52.00 + -85.25 = -187.75
    assert abs(jan_total - (-187.75)) < 0.01


def test_group_by_quarter(sample_transactions):
    """Test grouping by quarter."""
    result = finance_analysis.group_by_quarter(sample_transactions)

    assert 'quarter_start' in result.columns
    assert 'amount' in result.columns
    assert len(result) == 1  # All transactions in Q1 2025


def test_group_by_year(sample_transactions):
    """Test grouping by year."""
    result = finance_analysis.group_by_year(sample_transactions)

    assert 'year' in result.columns
    assert 'amount' in result.columns
    assert len(result) == 1  # All in 2025


def test_group_by_period(sample_transactions):
    """Test generic group by period function."""
    # Test with different periods
    monthly = finance_analysis.group_by_period(sample_transactions, 'month')
    assert 'month_start' in monthly.columns

    daily = finance_analysis.group_by_period(sample_transactions, 'day')
    assert 'date' in daily.columns

    # Test invalid period
    with pytest.raises(ValueError):
        finance_analysis.group_by_period(sample_transactions, 'invalid')


# ============================================================================
# CATEGORY ROLLUP TESTS
# ============================================================================

def test_calculate_category_totals(sample_transactions):
    """Test calculating totals by category."""
    result = finance_analysis.calculate_category_totals(sample_transactions)

    assert 'matched_category' in result.columns
    assert 'amount' in result.columns

    # Find coffee category
    coffee_row = result[result['matched_category'] == 'dining/coffee']
    assert len(coffee_row) == 1
    coffee_total = coffee_row.iloc[0]['amount']
    # -5.50 + -6.75 = -12.25
    assert abs(coffee_total - (-12.25)) < 0.01


def test_calculate_category_rollup(sample_transactions, sample_categories):
    """Test hierarchical category rollup."""
    # Test rolling up dining category
    dining_total = finance_analysis.calculate_category_rollup(
        sample_transactions,
        'dining',
        sample_categories
    )
    # dining/coffee: -12.25, dining/restaurants: -85.25 = -97.50
    assert abs(dining_total - (-97.50)) < 0.01

    # Test rolling up transportation category
    transport_total = finance_analysis.calculate_category_rollup(
        sample_transactions,
        'transportation',
        sample_categories
    )
    # transportation/rideshare: -45.00, transportation/car/gas: -100.00 = -145.00
    assert abs(transport_total - (-145.00)) < 0.01

    # Test leaf category (no descendants)
    coffee_total = finance_analysis.calculate_category_rollup(
        sample_transactions,
        'dining/coffee',
        sample_categories
    )
    assert abs(coffee_total - (-12.25)) < 0.01


def test_calculate_all_category_rollups(sample_transactions, sample_categories):
    """Test calculating rollups for all categories."""
    result = finance_analysis.calculate_all_category_rollups(
        sample_transactions,
        sample_categories
    )

    assert 'category_path' in result.columns
    assert 'amount' in result.columns
    assert 'level' in result.columns

    # Check root categories have correct rollups
    dining_row = result[result['category_path'] == 'dining']
    assert len(dining_row) == 1
    assert abs(dining_row.iloc[0]['amount'] - (-97.50)) < 0.01


# ============================================================================
# PERIOD COMPARISON TESTS
# ============================================================================

def test_calculate_period_change():
    """Test calculating change between periods."""
    # Test increase
    change = finance_analysis.calculate_period_change(120.0, 100.0)
    assert change['absolute_change'] == 20.0
    assert change['percent_change'] == 20.0

    # Test decrease
    change = finance_analysis.calculate_period_change(80.0, 100.0)
    assert change['absolute_change'] == -20.0
    assert change['percent_change'] == -20.0

    # Test from zero
    change = finance_analysis.calculate_period_change(100.0, 0.0)
    assert change['absolute_change'] == 100.0
    assert change['percent_change'] == 100.0


def test_compare_periods(sample_transactions):
    """Test comparing two time periods."""
    result = finance_analysis.compare_periods(
        sample_transactions,
        '2025-02-01', '2025-02-28',  # February
        '2025-01-01', '2025-01-31'   # January
    )

    assert 'current_amount' in result
    assert 'previous_amount' in result
    assert 'absolute_change' in result
    assert 'percent_change' in result

    # February: -6.75 + 3500.00 + -48.00 = 3445.25
    # January: -187.75
    assert abs(result['current_amount'] - 3445.25) < 0.01
    assert abs(result['previous_amount'] - (-187.75)) < 0.01


def test_compare_month_over_month(sample_transactions):
    """Test month-over-month comparison."""
    result = finance_analysis.compare_month_over_month(sample_transactions, 2025, 2)

    assert 'current_amount' in result
    assert 'previous_amount' in result

    # February vs January
    assert abs(result['current_amount'] - 3445.25) < 0.01
    assert abs(result['previous_amount'] - (-187.75)) < 0.01


# ============================================================================
# SUMMARY STATISTICS TESTS
# ============================================================================

def test_calculate_summary_statistics(sample_transactions):
    """Test calculating summary statistics."""
    stats = finance_analysis.calculate_summary_statistics(sample_transactions)

    assert 'total' in stats
    assert 'count' in stats
    assert 'mean' in stats
    assert 'total_income' in stats
    assert 'total_expenses' in stats
    assert 'net' in stats

    assert stats['count'] == 7
    assert stats['total_income'] == 3500.00
    # Expenses: -5.50 + -45.00 + -52.00 + -85.25 + -6.75 + -48.00 = -242.50
    assert abs(stats['total_expenses'] - (-242.50)) < 0.01
    # Net: 3500.00 - 242.50 = 3257.50
    assert abs(stats['net'] - 3257.50) < 0.01


def test_calculate_summary_statistics_empty():
    """Test summary statistics with empty DataFrame."""
    empty_df = pd.DataFrame(columns=['amount'])
    stats = finance_analysis.calculate_summary_statistics(empty_df)

    assert stats['count'] == 0
    assert stats['total'] == 0.0


def test_calculate_category_statistics(sample_transactions):
    """Test calculating statistics per category."""
    result = finance_analysis.calculate_category_statistics(sample_transactions)

    assert 'matched_category' in result.columns
    assert 'count' in result.columns
    assert 'total' in result.columns
    assert 'mean' in result.columns

    # Check coffee category
    coffee_row = result[result['matched_category'] == 'dining/coffee']
    assert len(coffee_row) == 1
    assert coffee_row.iloc[0]['count'] == 2  # 2 coffee transactions
    assert abs(coffee_row.iloc[0]['total'] - (-12.25)) < 0.01


# ============================================================================
# FILTERING TESTS
# ============================================================================

def test_filter_by_date_range(sample_transactions):
    """Test filtering by date range."""
    # Filter to January only
    jan_txns = finance_analysis.filter_by_date_range(
        sample_transactions,
        '2025-01-01',
        '2025-01-31'
    )
    assert len(jan_txns) == 4

    # Filter with only start date
    after_jan_20 = finance_analysis.filter_by_date_range(
        sample_transactions,
        start_date='2025-01-20'
    )
    assert len(after_jan_20) == 5  # Jan 22, Jan 30, Feb 5, Feb 10, Feb 15

    # Filter with only end date
    before_jan_20 = finance_analysis.filter_by_date_range(
        sample_transactions,
        end_date='2025-01-20'
    )
    assert len(before_jan_20) == 2  # Jan 15, Jan 16


def test_filter_by_category(sample_transactions, sample_categories):
    """Test filtering by category."""
    # Filter to dining (with descendants)
    dining_txns = finance_analysis.filter_by_category(
        sample_transactions,
        'dining',
        sample_categories,
        include_descendants=True
    )
    assert len(dining_txns) == 3  # coffee x2 + restaurants x1

    # Filter to dining (without descendants)
    dining_only = finance_analysis.filter_by_category(
        sample_transactions,
        'dining',
        sample_categories,
        include_descendants=False
    )
    assert len(dining_only) == 0  # No transactions directly in dining

    # Filter to transportation/car (with descendants)
    car_txns = finance_analysis.filter_by_category(
        sample_transactions,
        'transportation/car',
        sample_categories,
        include_descendants=True
    )
    assert len(car_txns) == 2  # gas x2


def test_filter_by_amount_range(sample_transactions):
    """Test filtering by amount range."""
    # Get only expenses (negative amounts)
    expenses = finance_analysis.filter_by_amount_range(
        sample_transactions,
        max_amount=-0.01
    )
    assert len(expenses) == 6

    # Get only income (positive amounts)
    income = finance_analysis.filter_by_amount_range(
        sample_transactions,
        min_amount=0.01
    )
    assert len(income) == 1

    # Get transactions between -50 and -10
    mid_range = finance_analysis.filter_by_amount_range(
        sample_transactions,
        min_amount=-50.0,
        max_amount=-10.0
    )
    assert len(mid_range) == 2  # -45.00 and -48.00


def test_filter_by_description(sample_transactions):
    """Test filtering by description."""
    # Case-insensitive search
    gas_txns = finance_analysis.filter_by_description(sample_transactions, 'gas')
    assert len(gas_txns) == 2

    coffee_txns = finance_analysis.filter_by_description(sample_transactions, 'coffee')
    assert len(coffee_txns) == 2

    # Case-sensitive search
    upper_gas = finance_analysis.filter_by_description(
        sample_transactions,
        'GAS',
        case_sensitive=True
    )
    assert len(upper_gas) == 2


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Running finance_analysis unit tests ===\n")
    print("To run all tests with pytest:")
    print("  pytest tests/finance/test_finance_analysis.py -v\n")
    print("Running pytest now...")

    # Run pytest programmatically
    pytest.main([__file__, "-v"])
