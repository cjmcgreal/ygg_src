"""
Business logic layer for the Table Editor.

Contains pure functions for:
- Unique value tracking and new value detection
- Column operations (add, delete, validate)

This module is framework-independent with no Streamlit dependencies.
All functions operate on pandas DataFrames and return new DataFrames
(immutable pattern) rather than modifying inputs in place.
"""

import pandas as pd
from typing import Dict, Set, List, Tuple, Any


# =============================================================================
# Unique Value Tracking
# =============================================================================

def get_unique_values(df: pd.DataFrame) -> Dict[str, Set]:
    """
    Extract unique values for each column in the DataFrame.

    Used to capture the initial state of a table when loaded, so that
    new values can be detected during editing.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary mapping column names to sets of unique values.
        Example: {'name': {'Alice', 'Bob'}, 'status': {'active', 'inactive'}}

    Example:
        >>> df = pd.DataFrame({'col': ['a', 'b', 'a']})
        >>> get_unique_values(df)
        {'col': {'a', 'b'}}
    """
    unique_values = {}

    for column in df.columns:
        # Convert column values to a set, handling NaN values
        # dropna() removes NaN values before creating the set
        values = set(df[column].dropna().unique())
        unique_values[column] = values

    return unique_values


def find_new_values(
    original_uniques: Dict[str, Set],
    edited_df: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Identify new values that appear in the edited DataFrame but not in original.

    Compares current values against the baseline captured at file load time.
    Used to trigger confirmation dialogs for new unique values.

    Args:
        original_uniques: Dictionary of original unique values per column
                         (from get_unique_values at load time)
        edited_df: Current state of the DataFrame after editing

    Returns:
        List of dicts with format: [{"column": str, "value": any}, ...]
        Each dict represents a new value that wasn't in the original data.

    Example:
        >>> original = {'status': {'active', 'inactive'}}
        >>> edited = pd.DataFrame({'status': ['active', 'pending']})
        >>> find_new_values(original, edited)
        [{'column': 'status', 'value': 'pending'}]
    """
    new_values = []

    for column in edited_df.columns:
        # Skip columns that didn't exist in original (newly added columns)
        if column not in original_uniques:
            continue

        original_set = original_uniques[column]
        current_values = set(edited_df[column].dropna().unique())

        # Find values in current that weren't in original
        added_values = current_values - original_set

        for value in added_values:
            new_values.append({
                'column': column,
                'value': value
            })

    return new_values


def has_new_values(
    original_uniques: Dict[str, Set],
    edited_df: pd.DataFrame
) -> bool:
    """
    Quick check if any new values exist in the edited DataFrame.

    Faster than find_new_values when you only need a boolean result.

    Args:
        original_uniques: Dictionary of original unique values per column
        edited_df: Current state of the DataFrame after editing

    Returns:
        True if any new values detected, False otherwise
    """
    for column in edited_df.columns:
        if column not in original_uniques:
            continue

        original_set = original_uniques[column]
        current_values = set(edited_df[column].dropna().unique())

        if current_values - original_set:
            return True

    return False


# =============================================================================
# Column Operations
# =============================================================================

def add_column(
    df: pd.DataFrame,
    column_name: str,
    default_value: str = ""
) -> pd.DataFrame:
    """
    Add a new text column to the DataFrame.

    Creates a copy of the DataFrame with the new column appended.
    Does not modify the original DataFrame.

    Args:
        df: DataFrame to add column to
        column_name: Name for the new column
        default_value: Value to fill in all rows (default: empty string)

    Returns:
        New DataFrame with the added column

    Raises:
        ValueError: If column_name already exists in DataFrame

    Example:
        >>> df = pd.DataFrame({'id': [1, 2]})
        >>> result = add_column(df, 'notes')
        >>> list(result.columns)
        ['id', 'notes']
    """
    # Validate column name doesn't already exist
    if column_name in df.columns:
        raise ValueError(f"Column '{column_name}' already exists")

    # Create a copy to avoid modifying original
    result_df = df.copy()

    # Add new column with default value
    result_df[column_name] = default_value

    return result_df


def delete_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Remove a column from the DataFrame.

    Creates a copy of the DataFrame with the specified column removed.
    Does not modify the original DataFrame.

    Args:
        df: DataFrame to remove column from
        column_name: Name of column to remove

    Returns:
        New DataFrame without the specified column

    Raises:
        KeyError: If column_name doesn't exist in DataFrame

    Example:
        >>> df = pd.DataFrame({'id': [1], 'temp': ['x']})
        >>> result = delete_column(df, 'temp')
        >>> list(result.columns)
        ['id']
    """
    # Validate column exists
    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found")

    # Create a copy and drop the column
    result_df = df.copy()
    result_df = result_df.drop(columns=[column_name])

    return result_df


def validate_column_name(
    df: pd.DataFrame,
    column_name: str
) -> Tuple[bool, str]:
    """
    Validate a proposed column name.

    Checks that the column name is valid for adding to the DataFrame:
    - Not empty
    - Doesn't already exist
    - Contains valid characters

    Args:
        df: DataFrame to validate against
        column_name: Proposed name for new column

    Returns:
        Tuple of (is_valid: bool, message: str)
        If invalid, message explains why. If valid, message is empty.

    Example:
        >>> df = pd.DataFrame({'id': [1]})
        >>> validate_column_name(df, 'id')
        (False, "Column 'id' already exists")
        >>> validate_column_name(df, 'new_col')
        (True, '')
    """
    # Check for empty name
    if not column_name or not column_name.strip():
        return (False, "Column name cannot be empty")

    # Normalize whitespace
    column_name = column_name.strip()

    # Check for duplicate
    if column_name in df.columns:
        return (False, f"Column '{column_name}' already exists")

    # Check for invalid characters (pandas is flexible, but we restrict)
    # Allow alphanumeric, underscore, space, and hyphen
    invalid_chars = set(column_name) - set(
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
        '_- '
    )
    if invalid_chars:
        return (False, f"Column name contains invalid characters: {invalid_chars}")

    return (True, '')


def rename_column(
    df: pd.DataFrame,
    old_name: str,
    new_name: str
) -> pd.DataFrame:
    """
    Rename a column in the DataFrame.

    Creates a copy of the DataFrame with the column renamed.
    Does not modify the original DataFrame.

    Args:
        df: DataFrame containing the column
        old_name: Current column name
        new_name: New column name

    Returns:
        New DataFrame with the column renamed

    Raises:
        KeyError: If old_name doesn't exist
        ValueError: If new_name already exists

    Example:
        >>> df = pd.DataFrame({'old': [1, 2]})
        >>> result = rename_column(df, 'old', 'new')
        >>> list(result.columns)
        ['new']
    """
    # Validate old column exists
    if old_name not in df.columns:
        raise KeyError(f"Column '{old_name}' not found")

    # Validate new name doesn't exist (unless same as old)
    if new_name != old_name and new_name in df.columns:
        raise ValueError(f"Column '{new_name}' already exists")

    # Create a copy and rename
    result_df = df.copy()
    result_df = result_df.rename(columns={old_name: new_name})

    return result_df


if __name__ == "__main__":
    """
    Standalone test section demonstrating business logic functionality.

    Run with: python table_editor_logic.py
    """
    print("=" * 60)
    print("Table Editor Logic - Standalone Test")
    print("=" * 60)

    # Create sample DataFrame for testing
    sample_df = pd.DataFrame({
        'id': [1, 2, 3, 4],
        'name': ['Alice', 'Bob', 'Alice', 'Charlie'],
        'status': ['active', 'inactive', 'active', 'active'],
        'score': [100, 200, 100, 300]
    })

    print("\nSample DataFrame:")
    print(sample_df)
    print()

    # Test 1: Get unique values
    print("1. Testing get_unique_values()...")
    unique_vals = get_unique_values(sample_df)
    print(f"   Unique values per column:")
    for col, vals in unique_vals.items():
        print(f"   - {col}: {vals}")

    # Test 2: Find new values
    print("\n2. Testing find_new_values()...")
    # Simulate editing - add a new status value
    edited_df = sample_df.copy()
    edited_df.loc[len(edited_df)] = [5, 'Diana', 'pending', 400]

    new_vals = find_new_values(unique_vals, edited_df)
    print(f"   New values detected: {len(new_vals)}")
    for item in new_vals:
        print(f"   - Column '{item['column']}': new value '{item['value']}'")

    # Test 3: Add column
    print("\n3. Testing add_column()...")
    df_with_new_col = add_column(sample_df, 'notes', default_value='N/A')
    print(f"   Original columns: {list(sample_df.columns)}")
    print(f"   After add_column: {list(df_with_new_col.columns)}")
    print(f"   New column values: {df_with_new_col['notes'].tolist()}")

    # Test 4: Delete column
    print("\n4. Testing delete_column()...")
    df_without_score = delete_column(sample_df, 'score')
    print(f"   Original columns: {list(sample_df.columns)}")
    print(f"   After delete_column: {list(df_without_score.columns)}")

    # Test 5: Validate column name
    print("\n5. Testing validate_column_name()...")
    test_names = ['new_col', 'id', '', 'col@name']
    for name in test_names:
        is_valid, msg = validate_column_name(sample_df, name)
        status = "VALID" if is_valid else f"INVALID: {msg}"
        print(f"   '{name}' -> {status}")

    # Test 6: has_new_values quick check
    print("\n6. Testing has_new_values()...")
    print(f"   Original vs same data: {has_new_values(unique_vals, sample_df)}")
    print(f"   Original vs edited data: {has_new_values(unique_vals, edited_df)}")

    print("\n" + "=" * 60)
    print("All standalone tests completed successfully!")
    print("=" * 60)
