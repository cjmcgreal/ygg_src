"""
finance_db.py - CSV Database Interface

Handles all CSV file reading and writing for the finance dashboard.
Provides CRUD-like functions for transactions, categories, label rules, and approvals.
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


# Database file paths
DATA_DIR = Path(__file__).parent / "finance_data"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"
CATEGORIES_FILE = DATA_DIR / "categories.csv"
LABEL_RULES_FILE = DATA_DIR / "label_rules.csv"
APPROVALS_FILE = DATA_DIR / "transaction_approvals.csv"


def ensure_data_dir_exists():
    """
    Ensure the finance_data directory exists.
    Creates it if it doesn't exist.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# TRANSACTIONS CRUD
# ============================================================================

def load_transactions() -> pd.DataFrame:
    """
    Load all transactions from CSV file.

    Returns:
        pd.DataFrame: Transactions with columns:
            - transaction_id (str): Unique identifier
            - date (str): Transaction date YYYY-MM-DD
            - description (str): Transaction description
            - amount (float): Amount (negative=expense, positive=income)
            - account (str): Account name (optional)
            - original_category (str): Original category from bank (optional)
            - import_date (str): Date imported into system

    Example:
        >>> df = load_transactions()
        >>> print(df.head())
    """
    if not TRANSACTIONS_FILE.exists():
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=[
            'transaction_id', 'date', 'description', 'amount',
            'account', 'original_category', 'import_date'
        ])

    df = pd.read_csv(TRANSACTIONS_FILE, dtype={
        'transaction_id': str,
        'date': str,
        'description': str,
        'amount': float,
        'account': str,
        'original_category': str,
        'import_date': str
    })

    # Handle empty file (just headers)
    if df.empty:
        return df

    # Ensure proper data types
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

    return df


def save_transactions(transactions_df: pd.DataFrame) -> bool:
    """
    Save transactions DataFrame to CSV file.

    Args:
        transactions_df (pd.DataFrame): Transactions to save

    Returns:
        bool: True if successful, False otherwise

    Example:
        >>> df = load_transactions()
        >>> # ... modify df ...
        >>> save_transactions(df)
    """
    try:
        ensure_data_dir_exists()
        transactions_df.to_csv(TRANSACTIONS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving transactions: {e}")
        return False


def add_transaction(transaction_id: str, date: str, description: str,
                   amount: float, account: str = "",
                   original_category: str = "") -> bool:
    """
    Add a new transaction to the database.

    Args:
        transaction_id (str): Unique transaction ID
        date (str): Transaction date YYYY-MM-DD
        description (str): Transaction description
        amount (float): Amount (negative for expenses)
        account (str): Account name (optional)
        original_category (str): Original category from bank (optional)

    Returns:
        bool: True if successful, False if transaction_id already exists

    Example:
        >>> add_transaction("txn_001", "2025-01-15", "Coffee Shop", -5.50)
    """
    df = load_transactions()

    # Check for duplicate transaction_id
    if not df.empty and transaction_id in df['transaction_id'].values:
        print(f"Transaction {transaction_id} already exists")
        return False

    # Create new transaction
    new_transaction = pd.DataFrame([{
        'transaction_id': transaction_id,
        'date': date,
        'description': description,
        'amount': amount,
        'account': account,
        'original_category': original_category,
        'import_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }])

    # Append and save
    df = pd.concat([df, new_transaction], ignore_index=True)
    return save_transactions(df)


def get_transaction_by_id(transaction_id: str) -> Optional[Dict]:
    """
    Get a specific transaction by ID.

    Args:
        transaction_id (str): Transaction ID to lookup

    Returns:
        dict or None: Transaction as dictionary, or None if not found

    Example:
        >>> txn = get_transaction_by_id("txn_001")
        >>> print(txn['description'])
    """
    df = load_transactions()

    if df.empty:
        return None

    matches = df[df['transaction_id'] == transaction_id]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def delete_transaction(transaction_id: str) -> bool:
    """
    Delete a transaction by ID.

    Args:
        transaction_id (str): Transaction ID to delete

    Returns:
        bool: True if deleted, False if not found

    Example:
        >>> delete_transaction("txn_001")
    """
    df = load_transactions()

    if df.empty:
        return False

    initial_len = len(df)
    df = df[df['transaction_id'] != transaction_id]

    if len(df) == initial_len:
        return False  # Transaction not found

    return save_transactions(df)


# ============================================================================
# CATEGORIES CRUD
# ============================================================================

def load_categories() -> pd.DataFrame:
    """
    Load all categories from CSV file.

    Returns:
        pd.DataFrame: Categories with columns:
            - category_id (str): Unique identifier
            - category_path (str): Full path (e.g., "transportation/car")
            - parent_category (str): Parent path (e.g., "transportation")
            - level (int): Hierarchy level (0=root)
            - display_name (str): Human-readable name
            - color (str): Color for visualization (hex code)

    Example:
        >>> df = load_categories()
        >>> print(df[df['level'] == 0])  # Show root categories
    """
    if not CATEGORIES_FILE.exists():
        return pd.DataFrame(columns=[
            'category_id', 'category_path', 'parent_category',
            'level', 'display_name', 'color'
        ])

    df = pd.read_csv(CATEGORIES_FILE, dtype={
        'category_id': str,
        'category_path': str,
        'parent_category': str,
        'level': int,
        'display_name': str,
        'color': str
    })

    # Ensure proper data types
    if not df.empty:
        df['level'] = pd.to_numeric(df['level'], errors='coerce').fillna(0).astype(int)
        # Convert NaN to empty string for parent_category (for root categories)
        df['parent_category'] = df['parent_category'].fillna('')

    return df


def save_categories(categories_df: pd.DataFrame) -> bool:
    """
    Save categories DataFrame to CSV file.

    Args:
        categories_df (pd.DataFrame): Categories to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_data_dir_exists()
        categories_df.to_csv(CATEGORIES_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving categories: {e}")
        return False


def add_category(category_id: str, category_path: str,
                parent_category: str = "", display_name: str = "",
                color: str = "#3498db") -> bool:
    """
    Add a new category to the database.

    Args:
        category_id (str): Unique category ID
        category_path (str): Full path (e.g., "transportation/car")
        parent_category (str): Parent path (empty for root categories)
        display_name (str): Human-readable name (defaults to last part of path)
        color (str): Hex color code (default: blue)

    Returns:
        bool: True if successful, False if category_id already exists

    Example:
        >>> add_category("cat_001", "transportation/car", "transportation", "Car Expenses")
    """
    df = load_categories()

    # Check for duplicate category_id
    if not df.empty and category_id in df['category_id'].values:
        print(f"Category {category_id} already exists")
        return False

    # Calculate level from parent_category
    level = 0 if not parent_category else parent_category.count('/') + 1

    # Default display_name to last part of path
    if not display_name:
        display_name = category_path.split('/')[-1].replace('_', ' ').title()

    # Create new category
    new_category = pd.DataFrame([{
        'category_id': category_id,
        'category_path': category_path,
        'parent_category': parent_category,
        'level': level,
        'display_name': display_name,
        'color': color
    }])

    # Append and save
    df = pd.concat([df, new_category], ignore_index=True)
    return save_categories(df)


def get_category_by_path(category_path: str) -> Optional[Dict]:
    """
    Get a category by its full path.

    Args:
        category_path (str): Full category path

    Returns:
        dict or None: Category as dictionary, or None if not found
    """
    df = load_categories()

    if df.empty:
        return None

    matches = df[df['category_path'] == category_path]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


# ============================================================================
# LABEL RULES CRUD
# ============================================================================

def load_label_rules() -> pd.DataFrame:
    """
    Load all label rules from CSV file.

    Returns:
        pd.DataFrame: Label rules with columns:
            - rule_id (str): Unique identifier
            - substring (str): Text to match in description
            - category_path (str): Category to assign
            - case_sensitive (bool): Whether matching is case-sensitive
            - priority (int): Rule priority (higher = checked first)
            - enabled (bool): Whether rule is active

    Example:
        >>> df = load_label_rules()
        >>> print(df.sort_values('priority', ascending=False))
    """
    if not LABEL_RULES_FILE.exists():
        return pd.DataFrame(columns=[
            'rule_id', 'substring', 'category_path',
            'case_sensitive', 'priority', 'enabled'
        ])

    df = pd.read_csv(LABEL_RULES_FILE, dtype={
        'rule_id': str,
        'substring': str,
        'category_path': str,
        'case_sensitive': bool,
        'priority': int,
        'enabled': bool
    })

    # Ensure proper data types
    if not df.empty:
        df['case_sensitive'] = df['case_sensitive'].astype(bool)
        df['priority'] = pd.to_numeric(df['priority'], errors='coerce').fillna(0).astype(int)
        df['enabled'] = df['enabled'].astype(bool)

    return df


def save_label_rules(rules_df: pd.DataFrame) -> bool:
    """
    Save label rules DataFrame to CSV file.

    Args:
        rules_df (pd.DataFrame): Label rules to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_data_dir_exists()
        rules_df.to_csv(LABEL_RULES_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving label rules: {e}")
        return False


def add_label_rule(rule_id: str, substring: str, category_path: str,
                  case_sensitive: bool = False, priority: int = 0,
                  enabled: bool = True) -> bool:
    """
    Add a new label rule to the database.

    Args:
        rule_id (str): Unique rule ID
        substring (str): Text to match in transaction description
        category_path (str): Category to assign when matched
        case_sensitive (bool): Whether matching is case-sensitive
        priority (int): Rule priority (higher = checked first)
        enabled (bool): Whether rule is active

    Returns:
        bool: True if successful, False if rule_id already exists

    Example:
        >>> add_label_rule("rule_001", "starbucks", "dining/coffee", priority=10)
    """
    df = load_label_rules()

    # Check for duplicate rule_id
    if not df.empty and rule_id in df['rule_id'].values:
        print(f"Rule {rule_id} already exists")
        return False

    # Create new rule
    new_rule = pd.DataFrame([{
        'rule_id': rule_id,
        'substring': substring,
        'category_path': category_path,
        'case_sensitive': case_sensitive,
        'priority': priority,
        'enabled': enabled
    }])

    # Append and save
    df = pd.concat([df, new_rule], ignore_index=True)
    return save_label_rules(df)


# ============================================================================
# TRANSACTION APPROVALS CRUD
# ============================================================================

def load_approvals() -> pd.DataFrame:
    """
    Load all transaction approvals from CSV file.

    Returns:
        pd.DataFrame: Approvals with columns:
            - transaction_id (str): Transaction ID (FK)
            - approved_category (str): Approved category path
            - approval_date (str): When approved (timestamp)
            - approval_method (str): How approved (auto/manual_edit/manual_accept)

    Example:
        >>> df = load_approvals()
        >>> approved_ids = df['transaction_id'].tolist()
    """
    if not APPROVALS_FILE.exists():
        return pd.DataFrame(columns=[
            'transaction_id', 'approved_category',
            'approval_date', 'approval_method'
        ])

    df = pd.read_csv(APPROVALS_FILE, dtype={
        'transaction_id': str,
        'approved_category': str,
        'approval_date': str,
        'approval_method': str
    })

    return df


def save_approvals(approvals_df: pd.DataFrame) -> bool:
    """
    Save approvals DataFrame to CSV file.

    Args:
        approvals_df (pd.DataFrame): Approvals to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_data_dir_exists()
        approvals_df.to_csv(APPROVALS_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving approvals: {e}")
        return False


def add_approval(transaction_id: str, approved_category: str,
                approval_method: str = "manual_accept") -> bool:
    """
    Add or update a transaction approval.

    If an approval already exists for this transaction, it will be updated.

    Args:
        transaction_id (str): Transaction ID to approve
        approved_category (str): Category to lock in
        approval_method (str): How approved (auto/manual_edit/manual_accept)

    Returns:
        bool: True if successful

    Example:
        >>> add_approval("txn_001", "dining/coffee", "manual_accept")
    """
    df = load_approvals()

    # Check if approval already exists
    if not df.empty and transaction_id in df['transaction_id'].values:
        # Update existing approval
        df.loc[df['transaction_id'] == transaction_id, 'approved_category'] = approved_category
        df.loc[df['transaction_id'] == transaction_id, 'approval_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df.loc[df['transaction_id'] == transaction_id, 'approval_method'] = approval_method
    else:
        # Create new approval
        new_approval = pd.DataFrame([{
            'transaction_id': transaction_id,
            'approved_category': approved_category,
            'approval_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'approval_method': approval_method
        }])

        df = pd.concat([df, new_approval], ignore_index=True)

    return save_approvals(df)


def get_approval_for_transaction(transaction_id: str) -> Optional[Dict]:
    """
    Get approval record for a specific transaction.

    Args:
        transaction_id (str): Transaction ID to lookup

    Returns:
        dict or None: Approval as dictionary, or None if not approved

    Example:
        >>> approval = get_approval_for_transaction("txn_001")
        >>> if approval:
        >>>     print(f"Approved as: {approval['approved_category']}")
    """
    df = load_approvals()

    if df.empty:
        return None

    matches = df[df['transaction_id'] == transaction_id]

    if matches.empty:
        return None

    return matches.iloc[0].to_dict()


def is_transaction_approved(transaction_id: str) -> bool:
    """
    Check if a transaction has been approved.

    Args:
        transaction_id (str): Transaction ID to check

    Returns:
        bool: True if approved, False otherwise

    Example:
        >>> if is_transaction_approved("txn_001"):
        >>>     print("Already approved - don't overwrite!")
    """
    return get_approval_for_transaction(transaction_id) is not None


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Finance DB Module Test ===\n")

    # Test 1: Add a transaction
    print("Test 1: Adding a transaction...")
    success = add_transaction(
        transaction_id="test_txn_001",
        date="2025-01-15",
        description="Starbucks Coffee",
        amount=-5.50,
        account="Chase Credit"
    )
    print(f"  Result: {'Success' if success else 'Failed'}")

    # Test 2: Load and display transaction
    print("\nTest 2: Loading transaction...")
    txn = get_transaction_by_id("test_txn_001")
    if txn:
        print(f"  Found: {txn['description']} for ${txn['amount']}")
    else:
        print("  Not found!")

    # Test 3: Add a category
    print("\nTest 3: Adding a category...")
    success = add_category(
        category_id="cat_001",
        category_path="dining/coffee",
        parent_category="dining",
        display_name="Coffee Shops"
    )
    print(f"  Result: {'Success' if success else 'Failed'}")

    # Test 4: Add a label rule
    print("\nTest 4: Adding a label rule...")
    success = add_label_rule(
        rule_id="rule_001",
        substring="starbucks",
        category_path="dining/coffee",
        priority=10
    )
    print(f"  Result: {'Success' if success else 'Failed'}")

    # Test 5: Add an approval
    print("\nTest 5: Approving transaction...")
    success = add_approval("test_txn_001", "dining/coffee", "manual_accept")
    print(f"  Result: {'Success' if success else 'Failed'}")

    # Test 6: Check if approved
    print("\nTest 6: Checking approval status...")
    is_approved = is_transaction_approved("test_txn_001")
    print(f"  Is approved: {is_approved}")
    if is_approved:
        approval = get_approval_for_transaction("test_txn_001")
        print(f"  Approved as: {approval['approved_category']}")

    # Test 7: Load all data
    print("\nTest 7: Loading all data...")
    transactions = load_transactions()
    categories = load_categories()
    rules = load_label_rules()
    approvals = load_approvals()
    print(f"  Transactions: {len(transactions)} rows")
    print(f"  Categories: {len(categories)} rows")
    print(f"  Label Rules: {len(rules)} rows")
    print(f"  Approvals: {len(approvals)} rows")

    # Cleanup
    print("\nTest 8: Cleanup...")
    delete_transaction("test_txn_001")
    print("  Test transaction deleted")

    print("\n=== All tests complete ===")
