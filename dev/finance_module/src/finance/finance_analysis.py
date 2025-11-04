"""
finance_analysis.py - Data Analysis Layer

Contains all data analysis and computational functions for the finance dashboard.
Handles time-based grouping, category rollups, comparisons, and statistics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta

# Handle imports for both module and standalone execution
try:
    from finance import finance_logic
except ImportError:
    import finance_logic


# ============================================================================
# TIME-BASED GROUPING
# ============================================================================

def group_by_day(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group transactions by day and calculate totals.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns

    Returns:
        pd.DataFrame: Grouped by date with sum of amounts

    Example:
        >>> daily_df = group_by_day(transactions_df)
        >>> print(daily_df[['date', 'amount']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=['date', 'amount'])

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Group by date and sum amounts
    grouped = df.groupby('date')['amount'].sum().reset_index()
    grouped = grouped.sort_values('date')

    return grouped


def group_by_week(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group transactions by week and calculate totals.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns

    Returns:
        pd.DataFrame: Grouped by week with sum of amounts and week_start date

    Example:
        >>> weekly_df = group_by_week(transactions_df)
        >>> print(weekly_df[['week_start', 'amount']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=['week_start', 'amount'])

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Get week start (Monday)
    df['week_start'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)

    # Group by week and sum amounts
    grouped = df.groupby('week_start')['amount'].sum().reset_index()
    grouped = grouped.sort_values('week_start')

    return grouped


def group_by_month(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group transactions by month and calculate totals.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns

    Returns:
        pd.DataFrame: Grouped by month with sum of amounts and month_start date

    Example:
        >>> monthly_df = group_by_month(transactions_df)
        >>> print(monthly_df[['month_start', 'amount']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=['month_start', 'amount'])

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Get month start
    df['month_start'] = df['date'].dt.to_period('M').apply(lambda r: r.start_time)

    # Group by month and sum amounts
    grouped = df.groupby('month_start')['amount'].sum().reset_index()
    grouped = grouped.sort_values('month_start')

    return grouped


def group_by_quarter(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group transactions by quarter and calculate totals.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns

    Returns:
        pd.DataFrame: Grouped by quarter with sum of amounts and quarter_start date

    Example:
        >>> quarterly_df = group_by_quarter(transactions_df)
        >>> print(quarterly_df[['quarter_start', 'amount']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=['quarter_start', 'amount'])

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Get quarter start
    df['quarter_start'] = df['date'].dt.to_period('Q').apply(lambda r: r.start_time)

    # Group by quarter and sum amounts
    grouped = df.groupby('quarter_start')['amount'].sum().reset_index()
    grouped = grouped.sort_values('quarter_start')

    return grouped


def group_by_year(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Group transactions by year and calculate totals.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns

    Returns:
        pd.DataFrame: Grouped by year with sum of amounts and year value

    Example:
        >>> yearly_df = group_by_year(transactions_df)
        >>> print(yearly_df[['year', 'amount']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=['year', 'amount'])

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Get year
    df['year'] = df['date'].dt.year

    # Group by year and sum amounts
    grouped = df.groupby('year')['amount'].sum().reset_index()
    grouped = grouped.sort_values('year')

    return grouped


def group_by_period(transactions_df: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Group transactions by specified period.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' and 'amount' columns
        period (str): One of 'day', 'week', 'month', 'quarter', 'year'

    Returns:
        pd.DataFrame: Grouped transactions

    Example:
        >>> monthly = group_by_period(transactions_df, 'month')
    """
    period_map = {
        'day': group_by_day,
        'week': group_by_week,
        'month': group_by_month,
        'quarter': group_by_quarter,
        'year': group_by_year
    }

    if period not in period_map:
        raise ValueError(f"Invalid period: {period}. Must be one of {list(period_map.keys())}")

    return period_map[period](transactions_df)


# ============================================================================
# CATEGORY ROLLUP CALCULATIONS
# ============================================================================

def calculate_category_totals(transactions_df: pd.DataFrame,
                              category_column: str = 'matched_category') -> pd.DataFrame:
    """
    Calculate total spending by category (leaf categories only).

    Args:
        transactions_df (pd.DataFrame): Transactions with category and amount columns
        category_column (str): Name of the category column

    Returns:
        pd.DataFrame: Categories with total amounts

    Example:
        >>> totals = calculate_category_totals(transactions_df)
        >>> print(totals.sort_values('amount'))
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=[category_column, 'amount'])

    # Filter out transactions without categories
    df = transactions_df[transactions_df[category_column].notna()].copy()

    if df.empty:
        return pd.DataFrame(columns=[category_column, 'amount'])

    # Group by category and sum amounts
    grouped = df.groupby(category_column)['amount'].sum().reset_index()
    grouped = grouped.sort_values('amount')

    return grouped


def calculate_category_rollup(transactions_df: pd.DataFrame,
                              parent_category: str,
                              categories_df: pd.DataFrame,
                              category_column: str = 'matched_category') -> float:
    """
    Calculate total spending for a category including all descendants.

    This is the key function for hierarchical rollups.

    Args:
        transactions_df (pd.DataFrame): Transactions with category column
        parent_category (str): Category to rollup (e.g., "transportation")
        categories_df (pd.DataFrame): All categories from database
        category_column (str): Name of the category column

    Returns:
        float: Total amount for category and all descendants

    Example:
        >>> # Get total transportation spending (includes car, air_travel, etc.)
        >>> total = calculate_category_rollup(txns, "transportation", cats)
    """
    if transactions_df.empty:
        return 0.0

    # Get all descendants of this category
    descendants = finance_logic.get_all_descendants(parent_category, categories_df)

    # Include the parent category itself
    all_categories = [parent_category] + descendants

    # Filter transactions to these categories
    df = transactions_df[
        transactions_df[category_column].isin(all_categories)
    ]

    # Sum amounts
    total = df['amount'].sum()

    return float(total)


def calculate_all_category_rollups(transactions_df: pd.DataFrame,
                                   categories_df: pd.DataFrame,
                                   category_column: str = 'matched_category') -> pd.DataFrame:
    """
    Calculate rollup totals for all categories.

    For each category, includes spending from that category and all descendants.

    Args:
        transactions_df (pd.DataFrame): Transactions with category column
        categories_df (pd.DataFrame): All categories from database
        category_column (str): Name of the category column

    Returns:
        pd.DataFrame: All categories with rollup amounts

    Example:
        >>> rollups = calculate_all_category_rollups(transactions_df, categories_df)
        >>> print(rollups[rollups['level'] == 0])  # Show root categories
    """
    if categories_df.empty:
        return pd.DataFrame(columns=['category_path', 'amount', 'level'])

    results = []

    for _, category in categories_df.iterrows():
        category_path = category['category_path']
        level = category['level']

        # Calculate rollup for this category
        rollup_amount = calculate_category_rollup(
            transactions_df,
            category_path,
            categories_df,
            category_column
        )

        results.append({
            'category_path': category_path,
            'amount': rollup_amount,
            'level': level,
            'display_name': category.get('display_name', category_path),
            'color': category.get('color', '#000000')
        })

    rollups_df = pd.DataFrame(results)
    rollups_df = rollups_df.sort_values('amount')

    return rollups_df


# ============================================================================
# PERIOD COMPARISON
# ============================================================================

def calculate_period_change(current_amount: float, previous_amount: float) -> Dict[str, float]:
    """
    Calculate change between two periods.

    Args:
        current_amount (float): Current period amount
        previous_amount (float): Previous period amount

    Returns:
        dict: Contains 'absolute_change', 'percent_change'

    Example:
        >>> change = calculate_period_change(100.0, 80.0)
        >>> print(f"Changed by {change['percent_change']:.1f}%")
    """
    absolute_change = current_amount - previous_amount

    if previous_amount == 0:
        # Avoid division by zero
        percent_change = 0.0 if current_amount == 0 else 100.0
    else:
        percent_change = (absolute_change / abs(previous_amount)) * 100

    return {
        'absolute_change': absolute_change,
        'percent_change': percent_change
    }


def compare_periods(transactions_df: pd.DataFrame,
                   current_start: str, current_end: str,
                   previous_start: str, previous_end: str) -> Dict[str, any]:
    """
    Compare spending between two time periods.

    Args:
        transactions_df (pd.DataFrame): All transactions
        current_start (str): Current period start date (YYYY-MM-DD)
        current_end (str): Current period end date (YYYY-MM-DD)
        previous_start (str): Previous period start date (YYYY-MM-DD)
        previous_end (str): Previous period end date (YYYY-MM-DD)

    Returns:
        dict: Comparison data including amounts and changes

    Example:
        >>> comparison = compare_periods(
        >>>     txns, '2025-02-01', '2025-02-28',
        >>>     '2025-01-01', '2025-01-31'
        >>> )
        >>> print(f"Spending changed by {comparison['percent_change']:.1f}%")
    """
    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    # Filter to current period
    current_df = df[
        (df['date'] >= current_start) &
        (df['date'] <= current_end)
    ]
    current_amount = current_df['amount'].sum()

    # Filter to previous period
    previous_df = df[
        (df['date'] >= previous_start) &
        (df['date'] <= previous_end)
    ]
    previous_amount = previous_df['amount'].sum()

    # Calculate change
    change = calculate_period_change(current_amount, previous_amount)

    return {
        'current_amount': current_amount,
        'previous_amount': previous_amount,
        'absolute_change': change['absolute_change'],
        'percent_change': change['percent_change'],
        'current_start': current_start,
        'current_end': current_end,
        'previous_start': previous_start,
        'previous_end': previous_end
    }


def compare_month_over_month(transactions_df: pd.DataFrame,
                            year: int, month: int) -> Dict[str, any]:
    """
    Compare a specific month to the previous month.

    Args:
        transactions_df (pd.DataFrame): All transactions
        year (int): Year of the month to analyze
        month (int): Month to analyze (1-12)

    Returns:
        dict: Month-over-month comparison

    Example:
        >>> # Compare February 2025 to January 2025
        >>> comparison = compare_month_over_month(transactions_df, 2025, 2)
    """
    # Calculate current month dates
    current_start = pd.Timestamp(year=year, month=month, day=1)
    if month == 12:
        current_end = pd.Timestamp(year=year, month=12, day=31)
        previous_start = pd.Timestamp(year=year, month=11, day=1)
        previous_end = pd.Timestamp(year=year, month=11, day=30)
    else:
        current_end = pd.Timestamp(year=year, month=month+1, day=1) - timedelta(days=1)
        if month == 1:
            previous_start = pd.Timestamp(year=year-1, month=12, day=1)
            previous_end = pd.Timestamp(year=year-1, month=12, day=31)
        else:
            previous_start = pd.Timestamp(year=year, month=month-1, day=1)
            previous_end = pd.Timestamp(year=year, month=month, day=1) - timedelta(days=1)

    return compare_periods(
        transactions_df,
        current_start.strftime('%Y-%m-%d'),
        current_end.strftime('%Y-%m-%d'),
        previous_start.strftime('%Y-%m-%d'),
        previous_end.strftime('%Y-%m-%d')
    )


# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

def calculate_summary_statistics(transactions_df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate summary statistics for transactions.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'amount' column

    Returns:
        dict: Summary statistics including total, mean, median, etc.

    Example:
        >>> stats = calculate_summary_statistics(transactions_df)
        >>> print(f"Average transaction: ${stats['mean']:.2f}")
    """
    if transactions_df.empty:
        return {
            'total': 0.0,
            'count': 0,
            'mean': 0.0,
            'median': 0.0,
            'std': 0.0,
            'min': 0.0,
            'max': 0.0,
            'total_income': 0.0,
            'total_expenses': 0.0,
            'net': 0.0
        }

    amounts = transactions_df['amount']

    # Separate income (positive) and expenses (negative)
    income = amounts[amounts > 0]
    expenses = amounts[amounts < 0]

    return {
        'total': float(amounts.sum()),
        'count': int(len(amounts)),
        'mean': float(amounts.mean()),
        'median': float(amounts.median()),
        'std': float(amounts.std()),
        'min': float(amounts.min()),
        'max': float(amounts.max()),
        'total_income': float(income.sum()) if len(income) > 0 else 0.0,
        'total_expenses': float(expenses.sum()) if len(expenses) > 0 else 0.0,
        'net': float(amounts.sum())
    }


def calculate_category_statistics(transactions_df: pd.DataFrame,
                                  category_column: str = 'matched_category') -> pd.DataFrame:
    """
    Calculate statistics for each category.

    Args:
        transactions_df (pd.DataFrame): Transactions with category and amount columns
        category_column (str): Name of the category column

    Returns:
        pd.DataFrame: Categories with statistics

    Example:
        >>> stats = calculate_category_statistics(transactions_df)
        >>> print(stats[['category', 'count', 'mean', 'total']])
    """
    if transactions_df.empty:
        return pd.DataFrame(columns=[category_column, 'count', 'total', 'mean'])

    # Filter out transactions without categories
    df = transactions_df[transactions_df[category_column].notna()].copy()

    if df.empty:
        return pd.DataFrame(columns=[category_column, 'count', 'total', 'mean'])

    # Group by category and calculate statistics
    stats = df.groupby(category_column)['amount'].agg([
        ('count', 'count'),
        ('total', 'sum'),
        ('mean', 'mean'),
        ('median', 'median'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).reset_index()

    stats = stats.sort_values('total')

    return stats


# ============================================================================
# FILTERING HELPERS
# ============================================================================

def filter_by_date_range(transactions_df: pd.DataFrame,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Filter transactions by date range.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'date' column
        start_date (str, optional): Start date (YYYY-MM-DD), inclusive
        end_date (str, optional): End date (YYYY-MM-DD), inclusive

    Returns:
        pd.DataFrame: Filtered transactions

    Example:
        >>> jan_txns = filter_by_date_range(txns, '2025-01-01', '2025-01-31')
    """
    if transactions_df.empty:
        return transactions_df

    df = transactions_df.copy()
    df['date'] = pd.to_datetime(df['date'])

    if start_date:
        df = df[df['date'] >= start_date]

    if end_date:
        df = df[df['date'] <= end_date]

    return df


def filter_by_category(transactions_df: pd.DataFrame,
                      category_path: str,
                      categories_df: pd.DataFrame,
                      include_descendants: bool = True,
                      category_column: str = 'matched_category') -> pd.DataFrame:
    """
    Filter transactions by category.

    Args:
        transactions_df (pd.DataFrame): Transactions
        category_path (str): Category to filter to
        categories_df (pd.DataFrame): All categories
        include_descendants (bool): Include child categories (default: True)
        category_column (str): Name of the category column

    Returns:
        pd.DataFrame: Filtered transactions

    Example:
        >>> # Get all transportation transactions (including subcategories)
        >>> transport = filter_by_category(txns, "transportation", cats)
    """
    if transactions_df.empty:
        return transactions_df

    if include_descendants:
        # Get all descendants
        descendants = finance_logic.get_all_descendants(category_path, categories_df)
        all_categories = [category_path] + descendants
    else:
        all_categories = [category_path]

    # Filter to these categories
    filtered = transactions_df[
        transactions_df[category_column].isin(all_categories)
    ]

    return filtered


def filter_by_amount_range(transactions_df: pd.DataFrame,
                           min_amount: Optional[float] = None,
                           max_amount: Optional[float] = None) -> pd.DataFrame:
    """
    Filter transactions by amount range.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'amount' column
        min_amount (float, optional): Minimum amount (inclusive)
        max_amount (float, optional): Maximum amount (inclusive)

    Returns:
        pd.DataFrame: Filtered transactions

    Example:
        >>> # Get large expenses (more than $100)
        >>> large = filter_by_amount_range(txns, max_amount=-100.0)
    """
    if transactions_df.empty:
        return transactions_df

    df = transactions_df.copy()

    if min_amount is not None:
        df = df[df['amount'] >= min_amount]

    if max_amount is not None:
        df = df[df['amount'] <= max_amount]

    return df


def filter_by_description(transactions_df: pd.DataFrame,
                         search_term: str,
                         case_sensitive: bool = False) -> pd.DataFrame:
    """
    Filter transactions by description search.

    Args:
        transactions_df (pd.DataFrame): Transactions with 'description' column
        search_term (str): Term to search for
        case_sensitive (bool): Whether search is case-sensitive

    Returns:
        pd.DataFrame: Filtered transactions

    Example:
        >>> starbucks_txns = filter_by_description(txns, "starbucks")
    """
    if transactions_df.empty:
        return transactions_df

    df = transactions_df.copy()

    if case_sensitive:
        mask = df['description'].str.contains(search_term, na=False)
    else:
        mask = df['description'].str.contains(search_term, case=False, na=False)

    return df[mask]


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Finance Analysis Module Test ===\n")

    # Create sample data
    sample_data = [
        {'transaction_id': '1', 'date': '2025-01-15', 'amount': -5.50, 'matched_category': 'dining/coffee'},
        {'transaction_id': '2', 'date': '2025-01-16', 'amount': -45.00, 'matched_category': 'transportation/rideshare'},
        {'transaction_id': '3', 'date': '2025-01-22', 'amount': -12.50, 'matched_category': 'dining/restaurants'},
        {'transaction_id': '4', 'date': '2025-02-05', 'amount': -6.75, 'matched_category': 'dining/coffee'},
        {'transaction_id': '5', 'date': '2025-02-10', 'amount': 1500.00, 'matched_category': 'income/salary'},
    ]
    transactions_df = pd.DataFrame(sample_data)

    # Test 1: Time grouping
    print("Test 1: Time-based grouping...")
    monthly = group_by_month(transactions_df)
    print(f"  Monthly totals:")
    for _, row in monthly.iterrows():
        print(f"    {row['month_start'].strftime('%Y-%m')}: ${row['amount']:.2f}")

    # Test 2: Summary statistics
    print("\nTest 2: Summary statistics...")
    stats = calculate_summary_statistics(transactions_df)
    print(f"  Total transactions: {stats['count']}")
    print(f"  Total income: ${stats['total_income']:.2f}")
    print(f"  Total expenses: ${stats['total_expenses']:.2f}")
    print(f"  Net: ${stats['net']:.2f}")

    # Test 3: Category totals
    print("\nTest 3: Category totals...")
    cat_totals = calculate_category_totals(transactions_df)
    print("  Spending by category:")
    for _, row in cat_totals.iterrows():
        print(f"    {row['matched_category']}: ${row['amount']:.2f}")

    # Test 4: Date filtering
    print("\nTest 4: Date filtering...")
    jan_txns = filter_by_date_range(transactions_df, '2025-01-01', '2025-01-31')
    print(f"  January transactions: {len(jan_txns)}")

    # Test 5: Amount filtering
    print("\nTest 5: Amount filtering...")
    expenses = filter_by_amount_range(transactions_df, max_amount=-0.01)
    print(f"  Expense transactions: {len(expenses)}")

    print("\n=== All tests complete ===")
