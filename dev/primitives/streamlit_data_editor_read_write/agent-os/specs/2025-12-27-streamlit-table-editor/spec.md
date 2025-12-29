# Specification: Streamlit Table Editor Primitive

## Goal

Build a reusable Streamlit-based CSV table editor that serves as a reference implementation ("primitive") for agents and developers. The editor uses `st.data_editor` for inline editing, provides unique value confirmation when new values are entered, and abstracts database operations behind a dedicated DB class to support future extension to PostgreSQL or other backends.

## User Stories

- As a user, I want to configure a working directory so that I can browse and select CSV files from my local filesystem
- As a user, I want to open CSV files directly from disk (not uploaded copies) so that I can edit the actual source files
- As a user, I want to see recently opened files with their timestamps so that I can quickly access files I've worked with before
- As a user, I want to add, edit, and delete rows in a table so that I can manage my data
- As a user, I want to add new columns (text type) to a table so that I can expand my data schema
- As a user, I want to delete columns with confirmation so that I don't accidentally lose data
- As a user, I want to be warned when entering a new unique value in a column so that I can catch typos or unintended new entries
- As a user, I want to toggle the unique value confirmation feature on/off so that I can work faster when I know what I'm doing
- As a user, I want explicit Save and Save As options so that I don't accidentally overwrite files

## Core Requirements

### Functional Requirements

**File Management**
- Text input in sidebar for configuring the working directory path
- Display list of all `.csv` files found in the working directory as a dropdown/selectbox
- Remember previously opened files with their absolute paths and last-modified timestamps
- Persist file history in a JSON file between sessions (no limit on number of files)
- Open files directly from disk, not as uploaded copies

**Table Editing (using st.data_editor)**
- Display loaded CSV data in `st.data_editor` widget
- Enable inline cell editing
- Support adding new rows (`num_rows="dynamic"`)
- Support deleting existing rows
- Support adding new columns (text-only for this version) via an "Add Column" button
- Support deleting columns with popup confirmation dialog

**Unique Value Confirmation Feature**
- Track unique values for each column when a table is loaded
- Compare edited values against the original unique value set
- When a new value is detected, show a popup/dialog asking user to confirm: "Value 'X' is new for column 'Y'. Add it?"
- Provide Confirm and Cancel options in the popup
- Toggle this feature on/off via a sidebar checkbox
- Store feature preference in session state

**Save Operations**
- Explicit "Save" button to overwrite the original CSV file
- "Save As" option that prompts for a new filename and saves to the working directory
- No auto-save functionality (to prevent accidental overwrites)
- Display success/error feedback after save operations

### Non-Functional Requirements

- **Extensibility**: DB class must be designed for potential swap to PostgreSQL, SQL, or other backends
- **Reusability**: DB class should be importable and usable by other processes
- **Clarity**: Code should be well-documented and serve as a reference implementation
- **Separation of Concerns**: Clear separation between UI layer (_app) and data layer (_db)
- **Performance**: Handle reasonably sized CSV files (hundreds to low thousands of rows)

## Visual Design

No visual mockups were provided. The UI follows a standard Streamlit layout:

**Sidebar Layout:**
- Working directory text input at top
- File selector dropdown (populated from working directory)
- Recently opened files section with timestamps
- Toggle checkbox for unique value confirmation feature

**Main Area Layout:**
- Title/header
- `st.data_editor` widget displaying the loaded CSV (full width)
- Action buttons row: "Add Column", "Save", "Save As"
- Status messages area for feedback

## Reusable Components

### Existing Code to Leverage

**Database Patterns:**
- `/home/conrad/git/ygg_src/src/domains/exercise/db.py`: Excellent reference for CSV-based database abstraction with `load_table()` and `save_table()` pattern, schema definitions, and CRUD operations
- Pattern: Use `pathlib.Path` for file operations
- Pattern: Return `pd.DataFrame` from load functions
- Pattern: Include `if __name__ == "__main__":` test sections

**Streamlit Patterns:**
- `/home/conrad/git/ygg_src/dev/social_media/post_selection_engine/src/selector/selector_app.py`: Reference for `st.data_editor` with disabled columns, session state management
- `/home/conrad/git/ygg_src/dev/task_management/task selection display/v1/task_man_app.py`: Simple `st.data_editor` with `num_rows="dynamic"` for adding rows
- Pattern: Use `render_{domain}()` function as main entry point
- Pattern: Initialize session state in dedicated function
- Pattern: Separate tab/section render functions

**UI Patterns:**
- `/home/conrad/git/ygg_src/src/domains/finance/src/datatable/datatable_app.py`: Reference for filter panels in expanders, dataframe display, download/export buttons

### New Components Required

**table_editor_db.py - Database Abstraction Layer**
- Generic CSV read/write operations abstracted behind an interface
- Must be reusable by other processes (not dependent on Streamlit)
- Designed for future extension to other database backends
- Functions: `load_csv()`, `save_csv()`, `list_csv_files()`, `get_file_metadata()`

**table_editor_logic.py - Business Logic**
- Unique value tracking and comparison logic
- Column operations (add/delete validation)
- New value detection for confirmation feature

**table_editor_app.py - Streamlit UI**
- Main `render_table_editor()` function
- Sidebar configuration rendering
- File history management
- Popup/dialog handling for confirmations

**File History Persistence**
- JSON file to store recently opened files
- Structure: list of `{path, last_opened, last_modified}` objects
- No third-party dependencies, use standard library json module

## Technical Approach

### Database Layer (table_editor_db.py)

The DB class should provide:
- `CSVDatabase` class or module-level functions for:
  - `load_csv(file_path: str) -> pd.DataFrame`
  - `save_csv(file_path: str, df: pd.DataFrame) -> bool`
  - `list_csv_files(directory: str) -> List[str]`
  - `get_file_info(file_path: str) -> Dict` (name, modified timestamp, size)
  - `file_exists(file_path: str) -> bool`
- Abstract interface that could be swapped for `PostgreSQLDatabase` in future

### Logic Layer (table_editor_logic.py)

- `get_unique_values(df: pd.DataFrame) -> Dict[str, Set]`: Extract unique values per column
- `find_new_values(original_uniques: Dict, edited_df: pd.DataFrame) -> List[Dict]`: Identify new values added during editing
- `add_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame`: Add empty text column
- `delete_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame`: Remove column

### Workflow Layer (table_editor_workflow.py)

Orchestration layer between UI and data:
- `open_file(file_path: str) -> Tuple[pd.DataFrame, Dict]`: Load file and return df + metadata
- `save_file(file_path: str, df: pd.DataFrame) -> bool`: Save with error handling
- `save_file_as(directory: str, filename: str, df: pd.DataFrame) -> str`: Save to new location
- `load_file_history() -> List[Dict]`: Load history from JSON
- `update_file_history(file_path: str) -> None`: Add/update file in history

### Frontend (table_editor_app.py)

- `render_table_editor()`: Main entry point
- `render_sidebar()`: Directory config, file selector, history, settings
- `render_editor()`: Main data editor and action buttons
- `handle_new_value_confirmation(new_values: List[Dict])`: Dialog for confirming new values
- Session state for: `current_file_path`, `current_df`, `original_unique_values`, `confirm_new_values_enabled`

### Streamlit Components to Use

- `st.sidebar`: Configuration panel
- `st.text_input`: Working directory path
- `st.selectbox`: File selector from directory
- `st.data_editor`: Main table editing widget with `num_rows="dynamic"`
- `st.checkbox`: Toggle for unique value confirmation
- `st.button`: Save, Save As, Add Column actions
- `st.dialog` or `st.modal` (via `@st.dialog` decorator): Confirmation popups
- `st.expander`: Recently opened files list
- `st.success/st.error/st.warning`: Feedback messages

### Data Persistence

- **File History**: `table_editor_history.json` in working directory or app config folder
  ```json
  {
    "files": [
      {
        "path": "/absolute/path/to/file.csv",
        "last_opened": "2025-12-27T10:30:00",
        "display_name": "file.csv"
      }
    ]
  }
  ```

### Testing Approach

- Test `_db.py` functions with sample CSV files
- Test `_logic.py` unique value detection with various dataframes
- Test `_workflow.py` orchestration with mocked db layer
- Each file includes `if __name__ == "__main__":` standalone test section

## Out of Scope

**Explicitly excluded from this version (but architecture should support future addition):**
- PostgreSQL/SQL database support (future extension via DB class interface)
- Multiple column data types beyond text (future: number, date, boolean)
- Undo/redo functionality
- Data validation rules beyond unique value confirmation
- Multi-file editing (only one file open at a time)
- Collaborative editing / concurrency handling
- Large file handling (streaming, pagination)
- Column reordering via drag-and-drop
- Column renaming (implement if straightforward with st.data_editor config)

## Success Criteria

- User can configure working directory and see CSV files listed
- User can open, edit, and save CSV files successfully
- New rows can be added and existing rows deleted
- New columns (text type) can be added via button
- Columns can be deleted with confirmation dialog
- Unique value confirmation popup appears when feature is enabled and new value detected
- File history persists between sessions and displays last-modified timestamps
- Code is well-documented and follows project structure conventions
- DB class is importable and usable independently of Streamlit UI
- All Python files include `if __name__ == "__main__":` test sections
