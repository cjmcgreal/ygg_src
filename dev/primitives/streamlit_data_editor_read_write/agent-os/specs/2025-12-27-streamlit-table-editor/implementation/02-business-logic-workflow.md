# Task 2: Business Logic and Workflow Orchestration

## Overview
**Task Reference:** Task #2 from `agent-os/specs/2025-12-27-streamlit-table-editor/tasks.md`
**Implemented By:** api-engineer
**Date:** 2025-12-27
**Status:** Complete

### Task Description
Implement the business logic layer (`table_editor_logic.py`) and workflow orchestration layer (`table_editor_workflow.py`) for the Streamlit Table Editor. The logic layer contains pure functions for unique value tracking and column operations. The workflow layer orchestrates between the database layer and the UI layer.

## Implementation Summary

The implementation provides a clean separation between business logic and workflow orchestration. The logic layer (`table_editor_logic.py`) contains pure functions that operate on pandas DataFrames without side effects, making them easy to test and reuse. Functions include unique value extraction, new value detection, and column manipulation (add, delete, rename, validate).

The workflow layer (`table_editor_workflow.py`) acts as the controller between the UI and database layers. It orchestrates file operations (open, save, save as), manages file history (load, update, format for display), and provides convenience functions for unique value confirmation workflows. All functions return tuples with success status and user-friendly messages, making error handling straightforward in the UI layer.

Both layers follow the immutable pattern where DataFrames are copied before modification, ensuring the original data remains unchanged. This design supports the undo/redo functionality that may be added in future versions.

## Files Changed/Created

### New Files
- `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_logic.py` - Business logic layer with pure functions for unique value tracking and column operations
- `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_workflow.py` - Workflow orchestration layer coordinating db and logic layers
- `/home/conrad/git/ygg_src/dev/primitives/tests/table_editor/test_table_editor_logic.py` - Unit tests for business logic functions

### Modified Files
- `/home/conrad/git/ygg_src/dev/primitives/agent-os/specs/2025-12-27-streamlit-table-editor/tasks.md` - Marked Task Group 2 as complete

## Key Implementation Details

### table_editor_logic.py - Unique Value Tracking
**Location:** `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_logic.py`

The unique value tracking system consists of three main functions:

1. `get_unique_values(df)` - Extracts unique values per column as a dictionary of sets. Handles NaN values by using `dropna()` before creating the set.

2. `find_new_values(original_uniques, edited_df)` - Compares current DataFrame values against the original baseline and returns a list of new values in the format `[{"column": str, "value": any}, ...]`.

3. `has_new_values(original_uniques, edited_df)` - A faster boolean check when you only need to know if changes exist.

**Rationale:** Using sets for unique value storage provides O(1) lookup for new value detection. The list-of-dicts return format from `find_new_values` allows the UI to easily iterate and display confirmation dialogs.

### table_editor_logic.py - Column Operations
**Location:** `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_logic.py`

Column operations follow an immutable pattern:

1. `add_column(df, column_name, default_value)` - Creates a copy and adds a new column with the specified default value.

2. `delete_column(df, column_name)` - Creates a copy and removes the specified column.

3. `validate_column_name(df, column_name)` - Returns a tuple `(is_valid, message)` checking for empty names, duplicates, and invalid characters.

4. `rename_column(df, old_name, new_name)` - Creates a copy and renames a column.

**Rationale:** The immutable pattern ensures the original DataFrame is never modified, which is important for implementing cancel/revert functionality and prevents accidental data loss.

### table_editor_workflow.py - File Operations Orchestration
**Location:** `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_workflow.py`

File operations wrap the database layer and add orchestration logic:

1. `open_file(file_path)` - Loads CSV and returns tuple `(DataFrame, metadata_dict)`.

2. `save_file(file_path, df)` - Saves with error handling, returns `(success, message)`.

3. `save_file_as(directory, filename, df)` - Creates new file with validation, returns `(success, message, new_path)`.

4. `list_available_files(directory)` - Lists CSV files with metadata for file selector dropdowns.

**Rationale:** The tuple return pattern provides both the operation result and a user-friendly message in a single call, simplifying UI code.

### table_editor_workflow.py - History Management
**Location:** `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_workflow.py`

History management provides persistence across sessions:

1. `load_file_history(history_path)` - Loads history from JSON.

2. `update_file_history(history_path, file_path)` - Adds or updates file entry with timestamp, maintains sorted order (most recent first).

3. `get_display_history(history)` - Formats history for UI display with human-readable timestamps and file existence checks.

4. `remove_from_history(history_path, file_path)` - Removes deleted files from history.

**Rationale:** Separating raw history loading from display formatting allows the UI layer to work with clean, pre-formatted data while maintaining flexibility in storage format.

### table_editor_workflow.py - Unique Value Confirmation Orchestration
**Location:** `/home/conrad/git/ygg_src/dev/primitives/src/table_editor/table_editor_workflow.py`

Convenience functions for the unique value confirmation workflow:

1. `capture_unique_values(df)` - Wraps logic layer function for use by UI.

2. `check_for_new_values(original_uniques, edited_df)` - Wraps logic layer for UI.

3. `has_unsaved_changes(original_uniques, edited_df)` - Quick boolean check.

4. `format_new_value_message(new_value)` - Formats messages for confirmation dialogs.

**Rationale:** These wrapper functions provide a clean API for the UI layer and allow future changes to the underlying logic without modifying UI code.

## Testing

### Test Files Created/Updated
- `/home/conrad/git/ygg_src/dev/primitives/tests/table_editor/test_table_editor_logic.py` - 4 focused unit tests

### Test Coverage
- Unit tests: Complete (4 tests)
- Integration tests: Partial (covered in workflow standalone tests)
- Edge cases covered:
  - Duplicate column names
  - Empty column names
  - New values in multiple columns
  - DataFrame immutability verification

### Manual Testing Performed
Both `table_editor_logic.py` and `table_editor_workflow.py` include comprehensive `if __name__ == "__main__":` sections that demonstrate all functionality:

1. Logic layer standalone test covers:
   - Unique value extraction
   - New value detection
   - Column add/delete operations
   - Column name validation
   - Quick change detection

2. Workflow layer standalone test covers:
   - File open/save/save-as operations
   - Unique value capture and detection
   - History management (add, update, remove)
   - Display history formatting

All standalone tests pass successfully.

### Test Results
```
tests/table_editor/test_table_editor_logic.py::TestUniqueValueTracking::test_get_unique_values_extracts_unique_values_per_column PASSED
tests/table_editor/test_table_editor_logic.py::TestUniqueValueTracking::test_find_new_values_identifies_new_values_vs_original PASSED
tests/table_editor/test_table_editor_logic.py::TestColumnOperations::test_add_column_adds_empty_text_column_to_dataframe PASSED
tests/table_editor/test_table_editor_logic.py::TestColumnOperations::test_delete_column_removes_column_from_dataframe PASSED

4 passed in 0.33s
```

## User Standards & Preferences Compliance

### Coding Style Standards
**File Reference:** `agent-os/standards/global/coding-style.md`

**How Your Implementation Complies:**
- Used descriptive function and variable names (e.g., `get_unique_values`, `find_new_values`, `original_uniques`)
- Functions are small and focused on a single task
- Consistent naming conventions with lowercase and underscores
- No dead code or commented-out blocks
- DRY principle followed - reusable functions extracted to logic layer

### Error Handling Standards
**File Reference:** `agent-os/standards/global/error-handling.md`

**How Your Implementation Complies:**
- User-friendly error messages returned in tuples (e.g., "Failed to save file. Please check permissions.")
- Fail fast pattern - validation occurs early in column operations
- Specific exception types used (ValueError, KeyError) for different error conditions
- Error handling at appropriate boundaries (workflow layer handles db layer errors)

### Validation Standards
**File Reference:** `agent-os/standards/global/validation.md`

**How Your Implementation Complies:**
- `validate_column_name()` provides specific field-level error messages
- Early validation before operations (check column exists before delete)
- Type and format validation for column names (alphanumeric, underscore, space, hyphen)
- Business rule validation in logic layer

### Test Writing Standards
**File Reference:** `agent-os/standards/testing/test-writing.md`

**How Your Implementation Complies:**
- Minimal focused tests (4 tests for core logic)
- Tests focus on behavior, not implementation
- Clear test names describe what is being tested
- External dependencies isolated using tempfile for test isolation
- Fast execution (0.33 seconds for all tests)

### CLAUDE.md Project Standards
**File Reference:** `/home/conrad/.claude/CLAUDE.md`

**How Your Implementation Complies:**
- Logic layer contains pure functions with no UI dependencies
- Workflow layer orchestrates between db and logic layers
- All functions have docstrings with Args, Returns, and Example
- `if __name__ == "__main__":` sections in both files for manual testing
- DataFrame operations use `.copy()` to avoid modifying original data
- Pandas DataFrames suffixed with `_df` for clarity in workflow layer

## Integration Points

### Internal Dependencies
- `table_editor_db.py` - CSVDatabase class for file I/O operations
- The workflow layer depends on the database layer but logic layer is independent

### API for UI Layer
The UI layer will use these workflow functions:
- `open_file()` - When user selects a file
- `save_file()` - When user clicks Save
- `save_file_as()` - When user clicks Save As
- `capture_unique_values()` - When file is loaded
- `check_for_new_values()` - After editing to detect changes
- `update_file_history()` - When file is opened
- `get_display_history()` - To populate sidebar history

## Known Issues & Limitations

### Limitations
1. **Set-based unique value tracking**
   - Description: Uses Python sets which don't preserve order
   - Reason: Order is not needed for new value detection, and sets provide O(1) lookup
   - Future Consideration: Could use ordered dict if order becomes important

2. **Simple change detection**
   - Description: Only detects new unique values, not deleted values or row changes
   - Reason: Spec only requires new value confirmation
   - Future Consideration: Could extend to track all types of changes

## Performance Considerations
- Unique value extraction uses `dropna().unique()` which is efficient for pandas DataFrames
- Set difference operations for new value detection are O(n) where n is the number of unique values
- History operations are O(n) where n is the number of history entries (typically small)

## Security Considerations
- File paths are used as-is without sanitization (assumes trusted input from UI)
- History JSON files could be tampered with but this is low risk for local tool

## Dependencies for Other Tasks
- Task Group 3 (UI Layer) depends on this implementation for:
  - File operations via workflow functions
  - Unique value confirmation via `check_for_new_values()`
  - History display via `get_display_history()`
  - Column operations via logic functions

## Notes
- The implementation follows an immutable pattern for DataFrame operations, which supports future undo/redo functionality
- Import handling supports both package imports (when used as part of table_editor module) and standalone execution (for testing)
- All workflow functions return consistent tuple formats for easy error handling in the UI
