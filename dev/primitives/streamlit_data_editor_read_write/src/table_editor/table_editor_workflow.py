"""
Workflow orchestration layer for the Table Editor.

Acts as the interface between the UI (app) layer and the backend (db, logic) layers.
Each user action in the UI maps to a function in this module.

This layer:
- Orchestrates calls to table_editor_db and table_editor_logic
- Handles error handling and message formatting
- Returns data in UI-friendly formats

Framework-independent - no Streamlit dependencies.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import pandas as pd

# Handle imports for both package and standalone execution
try:
    from table_editor.table_editor_db import CSVDatabase
    from table_editor.table_editor_logic import (
        get_unique_values,
        find_new_values,
        has_new_values
    )
except ImportError:
    # Fallback for standalone execution
    from table_editor_db import CSVDatabase
    from table_editor_logic import (
        get_unique_values,
        find_new_values,
        has_new_values
    )


# Default database instance for workflow operations
_db = CSVDatabase()


def get_db() -> CSVDatabase:
    """Get the database instance used by workflow functions."""
    return _db


# =============================================================================
# File Operations Orchestration
# =============================================================================

def open_file(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Open a CSV file and return DataFrame with metadata.

    Orchestrates loading the file and gathering file information
    for display in the UI.

    Args:
        file_path: Absolute path to the CSV file

    Returns:
        Tuple of (DataFrame, metadata_dict)
        metadata_dict contains: name, path, modified, size, exists

    Raises:
        FileNotFoundError: If file does not exist
        pd.errors.EmptyDataError: If file is empty

    Example:
        >>> df, meta = open_file('/path/to/data.csv')
        >>> print(f"Loaded {meta['name']} with {len(df)} rows")
    """
    db = get_db()

    # Load the CSV file (raises if not found)
    df = db.load_csv(file_path)

    # Get file metadata
    metadata = db.get_file_info(file_path)

    return (df, metadata)


def save_file(file_path: str, df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Save DataFrame to CSV file (overwrite existing).

    Used for the "Save" action to update the original file.

    Args:
        file_path: Absolute path to save the CSV file
        df: DataFrame to save

    Returns:
        Tuple of (success: bool, message: str)
        If success is False, message contains error description.

    Example:
        >>> success, msg = save_file('/path/to/data.csv', df)
        >>> if success:
        ...     print("File saved successfully")
    """
    db = get_db()

    try:
        result = db.save_csv(file_path, df)

        if result:
            return (True, f"File saved successfully: {Path(file_path).name}")
        else:
            return (False, "Failed to save file. Please check file permissions.")
    except Exception as e:
        return (False, f"Error saving file: {str(e)}")


def save_file_as(
    directory: str,
    filename: str,
    df: pd.DataFrame
) -> Tuple[bool, str, str]:
    """
    Save DataFrame to a new CSV file in the specified directory.

    Used for the "Save As" action to create a new file.

    Args:
        directory: Directory path to save the file in
        filename: Name for the new file (with or without .csv extension)
        df: DataFrame to save

    Returns:
        Tuple of (success: bool, message: str, new_file_path: str)
        new_file_path is the full path to the saved file.

    Example:
        >>> success, msg, path = save_file_as('/data', 'backup.csv', df)
        >>> if success:
        ...     print(f"Saved to: {path}")
    """
    db = get_db()

    # Ensure filename has .csv extension
    if not filename.lower().endswith('.csv'):
        filename = filename + '.csv'

    # Construct full path
    new_path = os.path.join(directory, filename)

    # Check if file already exists
    if db.file_exists(new_path):
        return (False, f"File '{filename}' already exists", new_path)

    try:
        result = db.save_csv(new_path, df)

        if result:
            return (True, f"File saved as: {filename}", new_path)
        else:
            return (False, "Failed to save file. Please check permissions.", new_path)
    except Exception as e:
        return (False, f"Error saving file: {str(e)}", new_path)


def list_available_files(directory: str) -> List[Dict[str, Any]]:
    """
    List all CSV files in a directory with their metadata.

    Used to populate the file selector dropdown in the UI.

    Args:
        directory: Path to directory to scan

    Returns:
        List of dicts with keys: name, path, modified, size
        Sorted alphabetically by filename.

    Example:
        >>> files = list_available_files('/data')
        >>> for f in files:
        ...     print(f"{f['name']} - {f['size']} bytes")
    """
    db = get_db()

    file_paths = db.list_csv_files(directory)

    files_info = []
    for path in file_paths:
        info = db.get_file_info(path)
        files_info.append(info)

    return files_info


# =============================================================================
# History Management
# =============================================================================

def load_file_history(history_path: str) -> List[Dict]:
    """
    Load file history from JSON persistence.

    Args:
        history_path: Path to the history JSON file

    Returns:
        List of file history entries (may be empty if no history)

    Example:
        >>> history = load_file_history('/app/.history.json')
        >>> print(f"Found {len(history)} recently opened files")
    """
    db = get_db()
    return db.load_history(history_path)


def update_file_history(
    history_path: str,
    file_path: str
) -> List[Dict]:
    """
    Add or update a file entry in the history.

    If the file already exists in history, updates its last_opened timestamp.
    If it's a new file, adds it to the history.

    Args:
        history_path: Path to the history JSON file
        file_path: Path to the file being opened

    Returns:
        Updated history list (most recently opened first)

    Example:
        >>> history = update_file_history('/app/.history.json', '/data/sales.csv')
        >>> print(f"Updated history with {len(history)} entries")
    """
    db = get_db()

    # Load existing history
    history = db.load_history(history_path)

    # Get file info for display name
    file_info = db.get_file_info(file_path)
    display_name = file_info['name']

    # Current timestamp
    now = datetime.now().isoformat()

    # Check if file already in history
    existing_entry = None
    for entry in history:
        if entry.get('path') == file_path:
            existing_entry = entry
            break

    if existing_entry:
        # Update existing entry
        existing_entry['last_opened'] = now
    else:
        # Add new entry
        history.append({
            'path': file_path,
            'last_opened': now,
            'display_name': display_name
        })

    # Sort by last_opened (most recent first)
    history.sort(key=lambda x: x.get('last_opened', ''), reverse=True)

    # Save updated history
    db.save_history(history_path, history)

    return history


def get_display_history(history: List[Dict]) -> List[Dict]:
    """
    Format history entries for display in the UI.

    Adds formatted timestamps and verifies file existence.

    Args:
        history: Raw history list from load_file_history()

    Returns:
        List of display-ready history entries with keys:
        - display_name: Filename to show
        - path: Full file path
        - last_opened_display: Human-readable timestamp
        - exists: Whether file still exists

    Example:
        >>> history = load_file_history(path)
        >>> display_history = get_display_history(history)
        >>> for h in display_history:
        ...     print(f"{h['display_name']} - {h['last_opened_display']}")
    """
    db = get_db()
    display_entries = []

    for entry in history:
        path = entry.get('path', '')
        last_opened = entry.get('last_opened', '')

        # Format the timestamp for display
        if last_opened:
            try:
                dt = datetime.fromisoformat(last_opened)
                # Format: "Dec 27, 2025 10:30 AM"
                last_opened_display = dt.strftime("%b %d, %Y %I:%M %p")
            except ValueError:
                last_opened_display = last_opened
        else:
            last_opened_display = "Unknown"

        # Check if file still exists
        exists = db.file_exists(path)

        display_entries.append({
            'display_name': entry.get('display_name', Path(path).name),
            'path': path,
            'last_opened_display': last_opened_display,
            'exists': exists
        })

    return display_entries


def remove_from_history(
    history_path: str,
    file_path: str
) -> List[Dict]:
    """
    Remove a file from the history.

    Useful for cleaning up entries for deleted files.

    Args:
        history_path: Path to the history JSON file
        file_path: Path of the file to remove from history

    Returns:
        Updated history list

    Example:
        >>> history = remove_from_history('/app/.history.json', '/data/old.csv')
    """
    db = get_db()

    # Load existing history
    history = db.load_history(history_path)

    # Remove the specified file
    history = [entry for entry in history if entry.get('path') != file_path]

    # Save updated history
    db.save_history(history_path, history)

    return history


# =============================================================================
# Unique Value Confirmation Orchestration
# =============================================================================

def check_for_new_values(
    original_uniques: Dict[str, set],
    edited_df: pd.DataFrame
) -> List[Dict]:
    """
    Check if the edited DataFrame contains any new unique values.

    Orchestrates the comparison between original and edited data.
    Called by the UI after editing to determine if confirmation is needed.

    Args:
        original_uniques: Dictionary of original unique values per column
                         (captured at file load time using capture_unique_values)
        edited_df: Current state of the DataFrame after editing

    Returns:
        List of new value entries: [{"column": str, "value": any}, ...]
        Empty list if no new values detected.

    Example:
        >>> original = capture_unique_values(df)
        >>> # ... user edits df ...
        >>> new_vals = check_for_new_values(original, edited_df)
        >>> if new_vals:
        ...     show_confirmation_dialog(new_vals)
    """
    return find_new_values(original_uniques, edited_df)


def capture_unique_values(df: pd.DataFrame) -> Dict[str, set]:
    """
    Capture baseline unique values for the DataFrame.

    Should be called when a file is first loaded to establish the baseline
    for new value detection.

    Args:
        df: DataFrame to capture unique values from

    Returns:
        Dictionary mapping column names to sets of unique values

    Example:
        >>> df, meta = open_file('/path/to/data.csv')
        >>> baseline = capture_unique_values(df)
        >>> # Store baseline in session state for later comparison
    """
    return get_unique_values(df)


def has_unsaved_changes(
    original_uniques: Dict[str, set],
    edited_df: pd.DataFrame
) -> bool:
    """
    Quick check if DataFrame has any changes from original.

    Faster than check_for_new_values when you only need a boolean.

    Args:
        original_uniques: Original unique values baseline
        edited_df: Current DataFrame state

    Returns:
        True if any changes detected, False otherwise
    """
    return has_new_values(original_uniques, edited_df)


def format_new_value_message(new_value: Dict) -> str:
    """
    Format a new value entry into a user-friendly message.

    Args:
        new_value: Dict with 'column' and 'value' keys

    Returns:
        Formatted message string

    Example:
        >>> msg = format_new_value_message({'column': 'status', 'value': 'pending'})
        >>> print(msg)
        "Value 'pending' is new for column 'status'"
    """
    column = new_value.get('column', 'unknown')
    value = new_value.get('value', '')

    return f"Value '{value}' is new for column '{column}'"


if __name__ == "__main__":
    """
    Standalone test section demonstrating workflow orchestration.

    Run with: python table_editor_workflow.py
    """
    import tempfile

    print("=" * 60)
    print("Table Editor Workflow - Standalone Test")
    print("=" * 60)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"\nUsing temp directory: {temp_dir}")

        # Create a sample CSV file
        sample_df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'status': ['active', 'inactive', 'active']
        })

        test_csv_path = os.path.join(temp_dir, 'test_data.csv')
        sample_df.to_csv(test_csv_path, index=False)

        # Test 1: Open file
        print("\n1. Testing open_file()...")
        df, metadata = open_file(test_csv_path)
        print(f"   Loaded: {metadata['name']}")
        print(f"   Size: {metadata['size']} bytes")
        print(f"   Rows: {len(df)}")

        # Test 2: Capture unique values
        print("\n2. Testing capture_unique_values()...")
        baseline = capture_unique_values(df)
        print(f"   Captured baseline for {len(baseline)} columns:")
        for col, vals in baseline.items():
            print(f"   - {col}: {vals}")

        # Test 3: Check for new values (no changes)
        print("\n3. Testing check_for_new_values() (no changes)...")
        new_vals = check_for_new_values(baseline, df)
        print(f"   New values found: {len(new_vals)}")

        # Test 4: Simulate editing and detect new values
        print("\n4. Testing new value detection after editing...")
        edited_df = df.copy()
        edited_df.loc[len(edited_df)] = [4, 'Diana', 'pending']

        new_vals = check_for_new_values(baseline, edited_df)
        print(f"   New values found: {len(new_vals)}")
        for val in new_vals:
            print(f"   - {format_new_value_message(val)}")

        # Test 5: Save file
        print("\n5. Testing save_file()...")
        success, msg = save_file(test_csv_path, edited_df)
        print(f"   Result: {'SUCCESS' if success else 'FAILED'}")
        print(f"   Message: {msg}")

        # Test 6: Save file as
        print("\n6. Testing save_file_as()...")
        success, msg, new_path = save_file_as(temp_dir, 'backup', edited_df)
        print(f"   Result: {'SUCCESS' if success else 'FAILED'}")
        print(f"   Message: {msg}")
        print(f"   New path: {new_path}")

        # Test 7: List available files
        print("\n7. Testing list_available_files()...")
        files = list_available_files(temp_dir)
        print(f"   Found {len(files)} CSV files:")
        for f in files:
            print(f"   - {f['name']}")

        # Test 8: File history management
        print("\n8. Testing history management...")
        history_path = os.path.join(temp_dir, '.history.json')

        # Update history with opened file
        history = update_file_history(history_path, test_csv_path)
        print(f"   After first file: {len(history)} entries")

        # Update with second file
        history = update_file_history(history_path, new_path)
        print(f"   After second file: {len(history)} entries")

        # Get display-ready history
        display_history = get_display_history(history)
        print("   Display history:")
        for h in display_history:
            exists_str = "exists" if h['exists'] else "MISSING"
            print(f"   - {h['display_name']} ({h['last_opened_display']}) [{exists_str}]")

        # Test 9: Remove from history
        print("\n9. Testing remove_from_history()...")
        history = remove_from_history(history_path, test_csv_path)
        print(f"   After removal: {len(history)} entries")

    print("\n" + "=" * 60)
    print("All standalone tests completed successfully!")
    print("=" * 60)
