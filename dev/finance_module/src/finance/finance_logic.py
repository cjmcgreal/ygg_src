"""
finance_logic.py - Business Logic Layer

Contains all custom business rules and logic for the finance dashboard.
Handles category hierarchy, substring matching, deduplication, and validation.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


# ============================================================================
# CATEGORY HIERARCHY PARSER
# ============================================================================

def parse_category_path(category_path: str) -> List[str]:
    """
    Parse a category path into its component parts.

    Args:
        category_path (str): Full category path (e.g., "transportation/car/gas")

    Returns:
        List[str]: List of path components ["transportation", "car", "gas"]

    Example:
        >>> parse_category_path("transportation/car/gas")
        ['transportation', 'car', 'gas']
    """
    if not category_path:
        return []

    return category_path.split('/')


def get_parent_category(category_path: str) -> str:
    """
    Get the parent category path from a full category path.

    Args:
        category_path (str): Full category path

    Returns:
        str: Parent path, or empty string if root category

    Example:
        >>> get_parent_category("transportation/car/gas")
        'transportation/car'
        >>> get_parent_category("transportation")
        ''
    """
    parts = parse_category_path(category_path)

    if len(parts) <= 1:
        return ""

    return '/'.join(parts[:-1])


def get_category_level(category_path: str) -> int:
    """
    Calculate the hierarchy level of a category.

    Args:
        category_path (str): Full category path

    Returns:
        int: Level (0 for root, 1 for first level, etc.)

    Example:
        >>> get_category_level("transportation")
        0
        >>> get_category_level("transportation/car/gas")
        2
    """
    if not category_path:
        return 0

    return category_path.count('/')


def get_all_children(category_path: str, all_categories_df: pd.DataFrame) -> List[str]:
    """
    Get all direct children of a category.

    Args:
        category_path (str): Parent category path
        all_categories_df (pd.DataFrame): All categories from database

    Returns:
        List[str]: List of child category paths

    Example:
        >>> children = get_all_children("transportation", categories_df)
        >>> # Returns: ["transportation/car", "transportation/air_travel", ...]
    """
    if all_categories_df.empty:
        return []

    # Find all categories where parent_category matches
    children = all_categories_df[
        all_categories_df['parent_category'] == category_path
    ]

    return children['category_path'].tolist()


def get_all_descendants(category_path: str, all_categories_df: pd.DataFrame) -> List[str]:
    """
    Get all descendants (children, grandchildren, etc.) of a category.

    Recursively traverses the hierarchy to find all nested subcategories.

    Args:
        category_path (str): Parent category path
        all_categories_df (pd.DataFrame): All categories from database

    Returns:
        List[str]: List of all descendant category paths

    Example:
        >>> descendants = get_all_descendants("transportation", categories_df)
        >>> # Returns: ["transportation/car", "transportation/car/gas",
        >>> #           "transportation/car/maintenance", "transportation/air_travel", ...]
    """
    descendants = []

    # Get direct children
    children = get_all_children(category_path, all_categories_df)

    for child in children:
        # Add child
        descendants.append(child)

        # Recursively get child's descendants
        child_descendants = get_all_descendants(child, all_categories_df)
        descendants.extend(child_descendants)

    return descendants


def get_category_ancestors(category_path: str) -> List[str]:
    """
    Get all ancestor categories (parent, grandparent, etc.) of a category.

    Args:
        category_path (str): Category path

    Returns:
        List[str]: List of ancestor paths from immediate parent to root

    Example:
        >>> get_category_ancestors("transportation/car/gas")
        ['transportation/car', 'transportation']
    """
    ancestors = []
    parts = parse_category_path(category_path)

    # Build ancestors from bottom to top
    for i in range(len(parts) - 1, 0, -1):
        ancestor = '/'.join(parts[:i])
        ancestors.append(ancestor)

    return ancestors


def is_descendant_of(child_path: str, parent_path: str) -> bool:
    """
    Check if a category is a descendant of another category.

    Args:
        child_path (str): Potential child category path
        parent_path (str): Potential parent category path

    Returns:
        bool: True if child_path is a descendant of parent_path

    Example:
        >>> is_descendant_of("transportation/car/gas", "transportation")
        True
        >>> is_descendant_of("dining/coffee", "transportation")
        False
    """
    if not parent_path:
        return True  # Everything is descendant of root

    # Child must start with parent path followed by "/"
    return child_path.startswith(parent_path + '/')


# ============================================================================
# SUBSTRING MATCHER
# ============================================================================

def match_transaction_to_category(description: str,
                                  label_rules_df: pd.DataFrame) -> Optional[str]:
    """
    Match a transaction description to a category using substring rules.

    Rules are checked in priority order (highest priority first).
    Only enabled rules are considered.

    Args:
        description (str): Transaction description to match
        label_rules_df (pd.DataFrame): Label rules from database

    Returns:
        str or None: Matched category path, or None if no match

    Example:
        >>> category = match_transaction_to_category("STARBUCKS #12345", rules_df)
        >>> # Returns: "dining/coffee"
    """
    if label_rules_df.empty or not description:
        return None

    # Filter to only enabled rules
    enabled_rules = label_rules_df[label_rules_df['enabled'] == True].copy()

    if enabled_rules.empty:
        return None

    # Sort by priority (highest first)
    enabled_rules = enabled_rules.sort_values('priority', ascending=False)

    # Check each rule in priority order
    for _, rule in enabled_rules.iterrows():
        substring = rule['substring']
        category_path = rule['category_path']
        case_sensitive = rule['case_sensitive']

        # Perform substring match
        if case_sensitive:
            # Case-sensitive match
            if substring in description:
                return category_path
        else:
            # Case-insensitive match
            if substring.lower() in description.lower():
                return category_path

    # No match found
    return None


def batch_match_transactions(transactions_df: pd.DataFrame,
                            label_rules_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply substring matching to a batch of transactions.

    Adds a 'matched_category' column to the transactions DataFrame.

    Args:
        transactions_df (pd.DataFrame): Transactions to match
        label_rules_df (pd.DataFrame): Label rules

    Returns:
        pd.DataFrame: Transactions with 'matched_category' column added

    Example:
        >>> matched_df = batch_match_transactions(transactions_df, rules_df)
        >>> print(matched_df[['description', 'matched_category']])
    """
    if transactions_df.empty:
        transactions_df['matched_category'] = None
        return transactions_df

    # Apply matching to each transaction
    transactions_df['matched_category'] = transactions_df['description'].apply(
        lambda desc: match_transaction_to_category(desc, label_rules_df)
    )

    return transactions_df


def get_unmatched_transactions(transactions_df: pd.DataFrame,
                               label_rules_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get all transactions that don't match any label rule.

    Useful for identifying transactions that need manual categorization.

    Args:
        transactions_df (pd.DataFrame): Transactions to check
        label_rules_df (pd.DataFrame): Label rules

    Returns:
        pd.DataFrame: Transactions with no category match

    Example:
        >>> unmatched = get_unmatched_transactions(transactions_df, rules_df)
        >>> print(f"Found {len(unmatched)} unmatched transactions")
    """
    matched_df = batch_match_transactions(
        transactions_df.copy(),
        label_rules_df
    )

    # Filter to rows where matched_category is None
    unmatched = matched_df[matched_df['matched_category'].isna()]

    return unmatched


# ============================================================================
# TRANSACTION DEDUPLICATION
# ============================================================================

def find_duplicate_transactions(new_transactions_df: pd.DataFrame,
                               existing_transactions_df: pd.DataFrame,
                               date_tolerance_days: int = 0,
                               amount_tolerance: float = 0.01) -> pd.DataFrame:
    """
    Find potential duplicate transactions.

    Compares new transactions against existing transactions based on:
    - Date (within tolerance window)
    - Amount (within tolerance)
    - Description (exact match or high similarity)

    Args:
        new_transactions_df (pd.DataFrame): New transactions to check
        existing_transactions_df (pd.DataFrame): Existing transactions
        date_tolerance_days (int): Days +/- to consider duplicate (default: 0 = exact date)
        amount_tolerance (float): Amount difference to consider duplicate (default: 0.01)

    Returns:
        pd.DataFrame: New transactions that are likely duplicates

    Example:
        >>> duplicates = find_duplicate_transactions(new_df, existing_df)
        >>> print(f"Found {len(duplicates)} potential duplicates")
    """
    if new_transactions_df.empty or existing_transactions_df.empty:
        return pd.DataFrame()

    duplicates = []

    for _, new_txn in new_transactions_df.iterrows():
        new_date = pd.to_datetime(new_txn['date'])
        new_amount = float(new_txn['amount'])
        new_desc = str(new_txn['description'])

        # Check against all existing transactions
        for _, existing_txn in existing_transactions_df.iterrows():
            existing_date = pd.to_datetime(existing_txn['date'])
            existing_amount = float(existing_txn['amount'])
            existing_desc = str(existing_txn['description'])

            # Check date within tolerance
            date_diff = abs((new_date - existing_date).days)
            if date_diff > date_tolerance_days:
                continue

            # Check amount within tolerance
            amount_diff = abs(new_amount - existing_amount)
            if amount_diff > amount_tolerance:
                continue

            # Check description exact match
            if new_desc == existing_desc:
                duplicates.append(new_txn)
                break  # Found duplicate, no need to check more

    if not duplicates:
        return pd.DataFrame()

    return pd.DataFrame(duplicates)


def deduplicate_transactions(transactions_df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate transactions from a DataFrame.

    Keeps the first occurrence of each unique transaction based on:
    - transaction_id (unique key)
    - Or combination of date, amount, and description

    Args:
        transactions_df (pd.DataFrame): Transactions to deduplicate

    Returns:
        pd.DataFrame: Deduplicated transactions

    Example:
        >>> clean_df = deduplicate_transactions(transactions_df)
        >>> print(f"Removed {len(transactions_df) - len(clean_df)} duplicates")
    """
    if transactions_df.empty:
        return transactions_df

    # First, remove duplicates by transaction_id
    deduped = transactions_df.drop_duplicates(subset=['transaction_id'], keep='first')

    # Then remove duplicates by date + amount + description
    deduped = deduped.drop_duplicates(
        subset=['date', 'amount', 'description'],
        keep='first'
    )

    return deduped


def generate_transaction_id(date: str, description: str, amount: float) -> str:
    """
    Generate a deterministic transaction ID from transaction details.

    This allows detecting duplicates even if imported multiple times.

    Args:
        date (str): Transaction date
        description (str): Transaction description
        amount (float): Transaction amount

    Returns:
        str: Generated transaction ID

    Example:
        >>> txn_id = generate_transaction_id("2025-01-15", "STARBUCKS", -5.50)
        >>> # Returns: "txn_2025-01-15_starbucks_-5.50"
    """
    # Create a normalized version of the description
    normalized_desc = description.lower().strip().replace(' ', '_')[:30]

    # Create ID from components
    txn_id = f"txn_{date}_{normalized_desc}_{amount}"

    return txn_id


# ============================================================================
# CATEGORY VALIDATOR
# ============================================================================

def is_valid_category_path(category_path: str) -> bool:
    """
    Validate that a category path is properly formatted.

    Rules:
    - Must not be empty
    - Must not start or end with "/"
    - Must not contain consecutive "//"
    - Must not contain special characters (only alphanumeric, underscore, and "/")

    Args:
        category_path (str): Category path to validate

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> is_valid_category_path("transportation/car")
        True
        >>> is_valid_category_path("/invalid/path")
        False
    """
    if not category_path:
        return False

    # Must not start or end with "/"
    if category_path.startswith('/') or category_path.endswith('/'):
        return False

    # Must not contain consecutive "//"
    if '//' in category_path:
        return False

    # Check each component
    parts = category_path.split('/')
    for part in parts:
        if not part:  # Empty component
            return False

        # Allow alphanumeric, underscore, hyphen, and space
        if not all(c.isalnum() or c in ('_', '-', ' ') for c in part):
            return False

    return True


def validate_parent_exists(category_path: str,
                          all_categories_df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that a category's parent exists in the database.

    Root categories (no parent) are always valid.

    Args:
        category_path (str): Category path to validate
        all_categories_df (pd.DataFrame): All existing categories

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> valid, msg = validate_parent_exists("transportation/car", categories_df)
        >>> if not valid:
        >>>     print(f"Error: {msg}")
    """
    parent_path = get_parent_category(category_path)

    # Root category - no parent needed
    if not parent_path:
        return True, ""

    # Check if parent exists
    if all_categories_df.empty:
        return False, f"Parent category '{parent_path}' does not exist"

    parent_exists = parent_path in all_categories_df['category_path'].values

    if not parent_exists:
        return False, f"Parent category '{parent_path}' does not exist"

    return True, ""


def validate_no_circular_dependency(category_path: str,
                                   parent_category: str,
                                   all_categories_df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that adding this category won't create a circular dependency.

    This prevents situations where A is parent of B, and B is parent of A.

    Args:
        category_path (str): New category path
        parent_category (str): Parent category path
        all_categories_df (pd.DataFrame): All existing categories

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> valid, msg = validate_no_circular_dependency("A", "B", categories_df)
    """
    if not parent_category:
        return True, ""  # Root category, no circular dependency possible

    # Check if parent_category is a descendant of category_path
    # This would create a circular dependency
    if is_descendant_of(parent_category, category_path):
        return False, f"Circular dependency: '{parent_category}' is already a child of '{category_path}'"

    return True, ""


def validate_category(category_path: str,
                     parent_category: str,
                     all_categories_df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Comprehensive validation for a category.

    Checks:
    - Path format is valid
    - Parent exists (if not root)
    - No circular dependencies
    - Parent matches category path structure

    Args:
        category_path (str): Category path to validate
        parent_category (str): Parent category path
        all_categories_df (pd.DataFrame): All existing categories

    Returns:
        Tuple[bool, str]: (is_valid, error_message)

    Example:
        >>> valid, msg = validate_category("transportation/car", "transportation", categories_df)
        >>> if not valid:
        >>>     print(f"Validation error: {msg}")
    """
    # Check path format
    if not is_valid_category_path(category_path):
        return False, f"Invalid category path format: '{category_path}'"

    # Check parent exists
    valid, msg = validate_parent_exists(category_path, all_categories_df)
    if not valid:
        return False, msg

    # Check no circular dependency
    valid, msg = validate_no_circular_dependency(
        category_path, parent_category, all_categories_df
    )
    if not valid:
        return False, msg

    # Verify parent matches path structure
    expected_parent = get_parent_category(category_path)
    if expected_parent != parent_category:
        return False, f"Parent mismatch: expected '{expected_parent}', got '{parent_category}'"

    return True, ""


# ============================================================================
# STANDALONE TEST SECTION
# ============================================================================

if __name__ == "__main__":
    print("=== Finance Logic Module Test ===\n")

    # Test 1: Category path parsing
    print("Test 1: Category path parsing...")
    path = "transportation/car/gas"
    parts = parse_category_path(path)
    parent = get_parent_category(path)
    level = get_category_level(path)
    print(f"  Path: {path}")
    print(f"  Parts: {parts}")
    print(f"  Parent: {parent}")
    print(f"  Level: {level}")

    # Test 2: Category hierarchy
    print("\nTest 2: Category ancestors...")
    ancestors = get_category_ancestors("transportation/car/gas")
    print(f"  Ancestors of 'transportation/car/gas': {ancestors}")

    # Test 3: Descendant check
    print("\nTest 3: Descendant check...")
    is_child = is_descendant_of("transportation/car/gas", "transportation")
    is_not_child = is_descendant_of("dining/coffee", "transportation")
    print(f"  'transportation/car/gas' is child of 'transportation': {is_child}")
    print(f"  'dining/coffee' is child of 'transportation': {is_not_child}")

    # Test 4: Substring matching
    print("\nTest 4: Substring matching...")

    # Create sample rules
    rules_data = [
        {'rule_id': '1', 'substring': 'starbucks', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 10, 'enabled': True},
        {'rule_id': '2', 'substring': 'coffee', 'category_path': 'dining/coffee',
         'case_sensitive': False, 'priority': 5, 'enabled': True},
        {'rule_id': '3', 'substring': 'uber', 'category_path': 'transportation/rideshare',
         'case_sensitive': False, 'priority': 15, 'enabled': True},
    ]
    rules_df = pd.DataFrame(rules_data)

    test_descriptions = [
        "STARBUCKS #12345",
        "UBER TRIP",
        "GENERIC COFFEE SHOP",
        "GROCERY STORE"
    ]

    for desc in test_descriptions:
        category = match_transaction_to_category(desc, rules_df)
        print(f"  '{desc}' -> {category}")

    # Test 5: Transaction ID generation
    print("\nTest 5: Transaction ID generation...")
    txn_id = generate_transaction_id("2025-01-15", "STARBUCKS COFFEE", -5.50)
    print(f"  Generated ID: {txn_id}")

    # Test 6: Path validation
    print("\nTest 6: Path validation...")
    valid_paths = ["transportation", "transportation/car", "dining/coffee"]
    invalid_paths = ["/invalid", "invalid/", "invalid//path", ""]

    print("  Valid paths:")
    for path in valid_paths:
        is_valid = is_valid_category_path(path)
        print(f"    '{path}': {is_valid}")

    print("  Invalid paths:")
    for path in invalid_paths:
        is_valid = is_valid_category_path(path)
        print(f"    '{path}': {is_valid}")

    print("\n=== All tests complete ===")
