# Task Breakdown: Streamlit Table Editor Primitive

## Overview
Total Tasks: 4 Task Groups (16 sub-tasks)
Assigned Implementers: database-engineer, api-engineer, ui-designer, testing-engineer

## Project Structure

Per CLAUDE.md standards, this feature will create the following files:
```
src/table_editor/
    table_editor_app.py      # Streamlit UI (render_table_editor)
    table_editor_workflow.py # API interface / orchestration layer
    table_editor_logic.py    # Business logic
    table_editor_db.py       # CSV database interface (reusable DB class)
    table_editor_data/       # Data folder for CSV files (sample data)

tests/table_editor/
    test_table_editor_app.py
    test_table_editor_workflow.py
    test_table_editor_logic.py
    test_table_editor_db.py
```

## Task List

### Data Layer

#### Task Group 1: CSV Database Abstraction Layer
**Assigned implementer:** database-engineer
**Dependencies:** None

- [x] 1.0 Complete CSV database abstraction layer (table_editor_db.py)
  - [x] 1.1 Write 2-4 focused tests for CSVDatabase class functionality
    - Test `load_csv()` reads CSV file and returns DataFrame
    - Test `save_csv()` writes DataFrame to CSV file
    - Test `list_csv_files()` returns list of CSV files in directory
    - Test `get_file_info()` returns file metadata (name, modified timestamp, size)
  - [x] 1.2 Create CSVDatabase class with abstract interface design
    - Design class to be swappable for PostgreSQLDatabase or other backends in future
    - Use `pathlib.Path` for all file operations
    - Make class importable and usable independently of Streamlit
  - [x] 1.3 Implement CSV read/write operations
    - `load_csv(file_path: str) -> pd.DataFrame`
    - `save_csv(file_path: str, df: pd.DataFrame) -> bool`
    - Handle encoding, missing files, and pandas DataFrame operations
  - [x] 1.4 Implement file system operations
    - `list_csv_files(directory: str) -> List[str]`
    - `get_file_info(file_path: str) -> Dict` (name, modified, size)
    - `file_exists(file_path: str) -> bool`
  - [x] 1.5 Implement file history persistence
    - `load_history(history_path: str) -> List[Dict]`
    - `save_history(history_path: str, history: List[Dict]) -> bool`
    - JSON format: `{"files": [{"path": str, "last_opened": str, "display_name": str}]}`
  - [x] 1.6 Add `if __name__ == "__main__":` standalone test section
    - Demonstrate usage of all CSVDatabase methods
    - Create sample CSV for manual testing
  - [x] 1.7 Ensure database layer tests pass
    - Run ONLY the 2-4 tests written in 1.1
    - Verify all CRUD operations work correctly

**Acceptance Criteria:**
- CSVDatabase class is importable and usable without Streamlit
- All CSV read/write operations work correctly
- File history loads and saves to JSON
- Class design allows future extension to other database backends
- The 2-4 tests from 1.1 pass

---

### Business Logic Layer

#### Task Group 2: Business Logic and Workflow Orchestration
**Assigned implementer:** api-engineer
**Dependencies:** Task Group 1

- [x] 2.0 Complete business logic and workflow layers
  - [x] 2.1 Write 2-4 focused tests for business logic
    - Test `get_unique_values()` extracts unique values per column
    - Test `find_new_values()` identifies new values vs original
    - Test `add_column()` adds empty text column to DataFrame
    - Test `delete_column()` removes column from DataFrame
  - [x] 2.2 Implement table_editor_logic.py - unique value tracking
    - `get_unique_values(df: pd.DataFrame) -> Dict[str, Set]`
    - `find_new_values(original_uniques: Dict, edited_df: pd.DataFrame) -> List[Dict]`
    - Return format: `[{"column": str, "value": any}, ...]`
  - [x] 2.3 Implement table_editor_logic.py - column operations
    - `add_column(df: pd.DataFrame, column_name: str, default_value: str = "") -> pd.DataFrame`
    - `delete_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame`
    - `validate_column_name(df: pd.DataFrame, column_name: str) -> Tuple[bool, str]`
  - [x] 2.4 Implement table_editor_workflow.py - file operations orchestration
    - `open_file(file_path: str) -> Tuple[pd.DataFrame, Dict]` (returns df + metadata)
    - `save_file(file_path: str, df: pd.DataFrame) -> Tuple[bool, str]` (returns success + message)
    - `save_file_as(directory: str, filename: str, df: pd.DataFrame) -> Tuple[bool, str, str]`
  - [x] 2.5 Implement table_editor_workflow.py - history management
    - `load_file_history(history_path: str) -> List[Dict]`
    - `update_file_history(history_path: str, file_path: str) -> List[Dict]`
    - `get_display_history(history: List[Dict]) -> List[Dict]` (formatted for UI)
  - [x] 2.6 Implement table_editor_workflow.py - unique value confirmation orchestration
    - `check_for_new_values(original_uniques: Dict, edited_df: pd.DataFrame) -> List[Dict]`
    - Orchestrates calls between logic and UI layers
  - [x] 2.7 Add `if __name__ == "__main__":` sections to both files
    - Demonstrate usage of all logic functions
    - Demonstrate workflow orchestration examples
  - [x] 2.8 Ensure logic and workflow tests pass
    - Run ONLY the 2-4 tests written in 2.1
    - Verify unique value detection works correctly

**Acceptance Criteria:**
- Unique value tracking correctly identifies new values
- Column add/delete operations work on DataFrames
- Workflow layer properly orchestrates between db and logic layers
- All functions have clear docstrings explaining purpose and usage
- The 2-4 tests from 2.1 pass

---

### UI Layer

#### Task Group 3: Streamlit UI Implementation
**Assigned implementer:** ui-designer
**Dependencies:** Task Groups 1, 2

- [x] 3.0 Complete Streamlit UI implementation (table_editor_app.py)
  - [x] 3.1 Write 2-4 focused tests for UI components
    - Test `render_table_editor()` function can be called without errors
    - Test session state initialization works correctly
    - Test sidebar renders with expected components
  - [x] 3.2 Implement session state initialization
    - `initialize_session_state()` function
    - State variables: `current_file_path`, `current_df`, `original_unique_values`, `confirm_new_values_enabled`, `file_history`, `working_directory`
  - [x] 3.3 Implement sidebar UI
    - Working directory text input (`st.text_input`)
    - File selector dropdown (`st.selectbox`) populated from working directory
    - Recently opened files section (`st.expander`) with timestamps
    - Unique value confirmation toggle (`st.checkbox`)
  - [x] 3.4 Implement main editor area
    - Title/header
    - `st.data_editor` widget with `num_rows="dynamic"` for the loaded CSV
    - Full width display of table
  - [x] 3.5 Implement action buttons
    - "Add Column" button with text input dialog for column name
    - "Delete Column" button/selector with confirmation dialog
    - "Save" button to overwrite original file
    - "Save As" button with filename input
  - [x] 3.6 Implement confirmation dialogs using `@st.dialog` decorator
    - New value confirmation popup: "Value 'X' is new for column 'Y'. Add it?"
    - Delete column confirmation popup: "Are you sure you want to delete column 'X'?"
    - Provide Confirm/Cancel options
  - [x] 3.7 Implement feedback messages
    - Success/error messages for save operations (`st.success`, `st.error`)
    - Warning messages for validation issues (`st.warning`)
    - Info messages for file loading (`st.info`)
  - [x] 3.8 Create main `render_table_editor()` entry point function
    - Orchestrate all UI components
    - Handle user interactions via workflow layer
    - Follow existing Streamlit patterns from spec.md references
  - [x] 3.9 Add `if __name__ == "__main__":` section
    - Allow running the app standalone with `streamlit run table_editor_app.py`
    - Initialize app configuration
  - [x] 3.10 Ensure UI components render without errors
    - Run ONLY the 2-4 tests written in 3.1
    - Manually verify UI renders correctly in browser

**Acceptance Criteria:**
- User can configure working directory and see CSV files listed
- User can open, edit cells, add/delete rows using st.data_editor
- User can add new columns via button
- User can delete columns with confirmation dialog
- Unique value confirmation popup appears when feature is enabled
- Save and Save As operations work with feedback messages
- File history displays in sidebar with timestamps
- The 2-4 tests from 3.1 pass

---

### Testing Layer

#### Task Group 4: Test Review and Integration Testing
**Assigned implementer:** testing-engineer
**Dependencies:** Task Groups 1, 2, 3

- [x] 4.0 Review existing tests and add critical integration tests
  - [x] 4.1 Review tests written by other implementers
    - Review 5 tests from database-engineer (Task 1.1)
    - Review 4 tests from api-engineer (Task 2.1)
    - Review 4 tests from ui-designer (Task 3.1)
    - Total existing tests: 13 tests
  - [x] 4.2 Analyze test coverage gaps for this feature only
    - Identify critical user workflows lacking test coverage
    - Focus on end-to-end workflows: open file -> edit -> save
    - Identify integration points between db, logic, workflow, and app layers
  - [x] 4.3 Write up to 6 additional strategic tests maximum
    - Test complete workflow: load CSV, detect changes, save file
    - Test unique value detection end-to-end
    - Test file history persistence across simulated sessions
    - Focus on integration between layers, not unit tests already covered
  - [x] 4.4 Create sample test data
    - Create `tests/table_editor/fixtures/` directory
    - Create sample CSV files for testing
    - Create sample history JSON for testing
  - [x] 4.5 Run all feature-specific tests
    - Run ONLY tests related to table_editor feature
    - Expected total: approximately 15-19 tests maximum
    - Verify all critical workflows pass
  - [x] 4.6 Document test coverage summary
    - List tested scenarios
    - Note any intentionally deferred edge cases

**Acceptance Criteria:**
- All feature-specific tests pass (approximately 15-19 tests total)
- Critical user workflows are covered by tests
- Integration between all layers is verified
- No more than 6 additional tests added by testing-engineer
- Test fixtures are available for future test additions

---

## Execution Order

Recommended implementation sequence:

1. **Task Group 1: CSV Database Abstraction Layer** (database-engineer)
   - Foundation layer that other components depend on
   - Must be complete before workflow and UI layers

2. **Task Group 2: Business Logic and Workflow Orchestration** (api-engineer)
   - Depends on database layer for file operations
   - Must be complete before UI layer can use it

3. **Task Group 3: Streamlit UI Implementation** (ui-designer)
   - Depends on both database and workflow layers
   - Final user-facing implementation

4. **Task Group 4: Test Review and Integration Testing** (testing-engineer)
   - Depends on all other layers being implemented
   - Validates complete feature works end-to-end

---

## Reference Files

Per spec.md, reference these existing patterns:

**Database Patterns:**
- `/home/conrad/git/ygg_src/src/domains/exercise/db.py` - CSV database abstraction pattern

**Streamlit Patterns:**
- `/home/conrad/git/ygg_src/dev/social_media/post_selection_engine/src/selector/selector_app.py` - st.data_editor with session state
- `/home/conrad/git/ygg_src/dev/task_management/task selection display/v1/task_man_app.py` - st.data_editor with num_rows="dynamic"

**UI Patterns:**
- `/home/conrad/git/ygg_src/src/domains/finance/src/datatable/datatable_app.py` - Filter panels, dataframe display
