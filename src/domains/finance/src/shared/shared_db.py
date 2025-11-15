"""
Shared database module for financial transactions.
Provides access to the mock transaction dataset used by all frontend styles.
"""

import pandas as pd
import os
from datetime import datetime, timedelta
import random


def get_data_path():
    """Get the path to the shared data directory."""
    # Point to the consolidated data folder at the domain root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    finance_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(finance_root, 'data')


def load_transactions():
    """
    Load financial transactions from CSV file.

    Returns:
        pd.DataFrame: Transaction data with columns:
            - transaction_id: Unique identifier
            - date: Transaction date
            - amount: Transaction amount (negative for expenses)
            - category: Transaction category
            - description: Transaction description
            - type: 'income' or 'expense'
    """
    data_path = get_data_path()
    csv_file = os.path.join(data_path, 'transactions.csv')

    if not os.path.exists(csv_file):
        # Generate mock data if file doesn't exist
        generate_mock_transactions()

    transactions_df = pd.read_csv(csv_file)

    # Convert date column to datetime
    transactions_df['date'] = pd.to_datetime(transactions_df['date'])

    return transactions_df


def generate_mock_transactions():
    """
    Generate mock financial transaction data and save to CSV.
    Creates 100 transactions over the past 6 months.
    """
    data_path = get_data_path()
    os.makedirs(data_path, exist_ok=True)
    csv_file = os.path.join(data_path, 'transactions.csv')

    # Transaction categories with typical amounts
    expense_categories = {
        'Groceries': (30, 150),
        'Dining': (15, 80),
        'Transportation': (20, 100),
        'Utilities': (50, 200),
        'Entertainment': (20, 150),
        'Healthcare': (50, 300),
        'Shopping': (25, 200),
        'Rent': (1000, 2000),
        'Insurance': (100, 400),
        'Subscriptions': (10, 50)
    }

    income_categories = {
        'Salary': (3000, 5000),
        'Freelance': (500, 2000),
        'Investment': (100, 1000),
        'Bonus': (500, 3000)
    }

    transactions = []
    start_date = datetime.now() - timedelta(days=180)  # 6 months ago

    # Generate 100 transactions
    for i in range(100):
        transaction_id = f"TXN{i+1:04d}"

        # Random date within the past 6 months
        random_days = random.randint(0, 180)
        transaction_date = start_date + timedelta(days=random_days)

        # 20% chance of income, 80% chance of expense
        is_income = random.random() < 0.2

        if is_income:
            category = random.choice(list(income_categories.keys()))
            amount_range = income_categories[category]
            amount = round(random.uniform(amount_range[0], amount_range[1]), 2)
            transaction_type = 'income'
            description = f"{category} payment"
        else:
            category = random.choice(list(expense_categories.keys()))
            amount_range = expense_categories[category]
            amount = -round(random.uniform(amount_range[0], amount_range[1]), 2)
            transaction_type = 'expense'
            description = f"{category} purchase"

        transactions.append({
            'transaction_id': transaction_id,
            'date': transaction_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'category': category,
            'description': description,
            'type': transaction_type
        })

    # Create DataFrame and save to CSV
    transactions_df = pd.DataFrame(transactions)
    transactions_df = transactions_df.sort_values('date')
    transactions_df.to_csv(csv_file, index=False)

    print(f"Generated {len(transactions)} mock transactions")


if __name__ == "__main__":
    # Generate and display sample data
    print("Generating mock financial transactions...")
    generate_mock_transactions()

    print("\nLoading transactions...")
    df = load_transactions()

    print(f"\nTotal transactions: {len(df)}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"\nTransaction types:")
    print(df['type'].value_counts())
    print(f"\nCategories:")
    print(df['category'].value_counts())
    print(f"\nSample transactions:")
    print(df.head(10))
    print(f"\nTotal income: ${df[df['type'] == 'income']['amount'].sum():,.2f}")
    print(f"Total expenses: ${abs(df[df['type'] == 'expense']['amount'].sum()):,.2f}")
