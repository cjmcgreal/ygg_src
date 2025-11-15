"""
Shared analysis functions for financial transaction data.
Used by all frontend styles to compute metrics and aggregations.
"""

import pandas as pd
from datetime import datetime


def calculate_balance(transactions_df):
    """
    Calculate running balance over time.

    Args:
        transactions_df (pd.DataFrame): Transaction data

    Returns:
        float: Current balance (sum of all transactions)
    """
    return transactions_df['amount'].sum()


def calculate_monthly_summary(transactions_df):
    """
    Calculate monthly income, expenses, and net for each month.

    Args:
        transactions_df (pd.DataFrame): Transaction data

    Returns:
        pd.DataFrame: Monthly summary with columns:
            - month: Month as datetime
            - income: Total income for month
            - expenses: Total expenses (positive number)
            - net: Net income/expense for month
            - transaction_count: Number of transactions
    """
    # Create copy to avoid modifying original
    df = transactions_df.copy()

    # Extract month from date
    df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()

    # Calculate income and expenses separately
    monthly_income = df[df['type'] == 'income'].groupby('month')['amount'].sum()
    monthly_expenses = df[df['type'] == 'expense'].groupby('month')['amount'].sum().abs()
    monthly_count = df.groupby('month').size()

    # Combine into summary DataFrame
    summary_df = pd.DataFrame({
        'month': monthly_income.index.union(monthly_expenses.index),
    })

    summary_df['income'] = summary_df['month'].map(monthly_income).fillna(0)
    summary_df['expenses'] = summary_df['month'].map(monthly_expenses).fillna(0)
    summary_df['net'] = summary_df['income'] - summary_df['expenses']
    summary_df['transaction_count'] = summary_df['month'].map(monthly_count).fillna(0).astype(int)

    return summary_df.sort_values('month')


def calculate_category_totals(transactions_df):
    """
    Calculate total spending/income by category.

    Args:
        transactions_df (pd.DataFrame): Transaction data

    Returns:
        pd.DataFrame: Category totals with columns:
            - category: Category name
            - total: Total amount (negative for expenses, positive for income)
            - transaction_count: Number of transactions
            - average: Average transaction amount
    """
    category_df = transactions_df.groupby('category').agg({
        'amount': ['sum', 'count', 'mean']
    }).reset_index()

    # Flatten column names
    category_df.columns = ['category', 'total', 'transaction_count', 'average']

    # Sort by absolute total (largest spending/earning first)
    category_df['abs_total'] = category_df['total'].abs()
    category_df = category_df.sort_values('abs_total', ascending=False)
    category_df = category_df.drop('abs_total', axis=1)

    return category_df


def calculate_daily_balance(transactions_df):
    """
    Calculate cumulative balance for each day.

    Args:
        transactions_df (pd.DataFrame): Transaction data

    Returns:
        pd.DataFrame: Daily balance with columns:
            - date: Transaction date
            - daily_total: Sum of transactions on that date
            - cumulative_balance: Running balance up to that date
    """
    # Group by date and sum transactions
    daily_df = transactions_df.groupby('date')['amount'].sum().reset_index()
    daily_df.columns = ['date', 'daily_total']

    # Calculate cumulative balance
    daily_df['cumulative_balance'] = daily_df['daily_total'].cumsum()

    return daily_df


def get_top_transactions(transactions_df, n=10, transaction_type='expense'):
    """
    Get the top N transactions by amount.

    Args:
        transactions_df (pd.DataFrame): Transaction data
        n (int): Number of top transactions to return
        transaction_type (str): 'expense' or 'income'

    Returns:
        pd.DataFrame: Top N transactions sorted by amount
    """
    # Filter by type
    filtered_df = transactions_df[transactions_df['type'] == transaction_type].copy()

    # Sort by absolute amount (largest first)
    filtered_df['abs_amount'] = filtered_df['amount'].abs()
    filtered_df = filtered_df.sort_values('abs_amount', ascending=False)

    # Return top N
    return filtered_df.head(n).drop('abs_amount', axis=1)


def calculate_statistics(transactions_df):
    """
    Calculate various statistics about transactions.

    Args:
        transactions_df (pd.DataFrame): Transaction data

    Returns:
        dict: Dictionary with statistical metrics
    """
    income_df = transactions_df[transactions_df['type'] == 'income']
    expense_df = transactions_df[transactions_df['type'] == 'expense']

    stats = {
        'total_transactions': len(transactions_df),
        'total_income': income_df['amount'].sum(),
        'total_expenses': abs(expense_df['amount'].sum()),
        'net_balance': transactions_df['amount'].sum(),
        'avg_income': income_df['amount'].mean() if len(income_df) > 0 else 0,
        'avg_expense': abs(expense_df['amount'].mean()) if len(expense_df) > 0 else 0,
        'largest_income': income_df['amount'].max() if len(income_df) > 0 else 0,
        'largest_expense': abs(expense_df['amount'].min()) if len(expense_df) > 0 else 0,
        'income_count': len(income_df),
        'expense_count': len(expense_df),
        'unique_categories': transactions_df['category'].nunique(),
    }

    return stats


if __name__ == "__main__":
    # Example usage with mock data
    from shared_db import load_transactions

    print("Loading transactions...")
    df = load_transactions()

    print("\n=== STATISTICS ===")
    stats = calculate_statistics(df)
    for key, value in stats.items():
        if 'total' in key or 'avg' in key or 'largest' in key or 'balance' in key:
            print(f"{key}: ${value:,.2f}")
        else:
            print(f"{key}: {value}")

    print("\n=== MONTHLY SUMMARY ===")
    monthly = calculate_monthly_summary(df)
    print(monthly)

    print("\n=== CATEGORY TOTALS ===")
    categories = calculate_category_totals(df)
    print(categories)

    print("\n=== TOP 5 EXPENSES ===")
    top_expenses = get_top_transactions(df, n=5, transaction_type='expense')
    print(top_expenses[['date', 'category', 'amount', 'description']])

    print("\n=== CURRENT BALANCE ===")
    balance = calculate_balance(df)
    print(f"${balance:,.2f}")
