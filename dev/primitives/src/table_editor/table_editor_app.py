"""
Streamlit UI for the Table Editor.

Provides a CSV table editor with:
- Working directory configuration
- File selection from directory
- Inline cell editing with st.data_editor
- Add/delete row support (num_rows="dynamic")
- Add/delete column functionality
- Unique value confirmation dialogs
- Save and Save As operations
- File history tracking

Main entry point: render_table_editor()
"""

import os
import sys
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import Optional

# Page config must be the first Streamlit command
# Check if we're running as the main script (not imported as a module)
if __name__ == "__main__":
    st.set_page_config(
        page_title="Table Editor",
        page_icon=":",
        layout="wide"
    )

# Handle imports for both package and standalone execution
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if str(_current_dir.parent) not in sys.path:
    sys.path.insert(0, str(_current_dir.parent))

try:
    from table_editor import table_editor_workflow as workflow
    from table_editor.table_editor_logic import (
        add_column,
        delete_column,
        validate_column_name
    )
except ImportError:
    import table_editor_workflow as workflow
    from table_editor_logic import (
        add_column,
        delete_column,
        validate_column_name
    )


# Default paths for the application
DEFAULT_WORKING_DIR = str(Path(__file__).parent / "table_editor_data")
HISTORY_FILENAME = ".table_editor_history.json"


# =============================================================================
# Session State Initialization
# =============================================================================

def initialize_session_state():
    """
    Initialize Streamlit session state variables for the table editor.

    State variables:
    - current_file_path: Path to currently loaded file
    - current_df: DataFrame currently being edited
    - original_unique_values: Baseline unique values for new value detection
    - confirm_new_values_enabled: Toggle for unique value confirmation feature
    - file_history: List of recently opened files
    - working_directory: Current working directory path
    """
    if 'current_file_path' not in st.session_state:
        st.session_state.current_file_path = None

    if 'current_df' not in st.session_state:
        st.session_state.current_df = None

    if 'original_unique_values' not in st.session_state:
        st.session_state.original_unique_values = {}

    if 'confirm_new_values_enabled' not in st.session_state:
        st.session_state.confirm_new_values_enabled = False

    if 'file_history' not in st.session_state:
        st.session_state.file_history = []

    if 'working_directory' not in st.session_state:
        st.session_state.working_directory = DEFAULT_WORKING_DIR

    # State for pending confirmations
    if 'pending_new_values' not in st.session_state:
        st.session_state.pending_new_values = []

    if 'column_to_delete' not in st.session_state:
        st.session_state.column_to_delete = None


def get_history_path() -> str:
    """Get the path for the history JSON file in the working directory."""
    return os.path.join(st.session_state.working_directory, HISTORY_FILENAME)


# =============================================================================
# Confirmation Dialogs
# =============================================================================

@st.dialog("New Value Detected")
def new_value_confirmation_dialog(new_value: dict):
    """
    Dialog to confirm adding a new unique value to a column.

    Args:
        new_value: Dict with 'column' and 'value' keys
    """
    column = new_value.get('column', 'unknown')
    value = new_value.get('value', '')

    st.write(f"Value **'{value}'** is new for column **'{column}'**.")
    st.write("Do you want to add it?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", type="primary", use_container_width=True):
            # Add value to original uniques so it won't trigger again
            if column in st.session_state.original_unique_values:
                st.session_state.original_unique_values[column].add(value)
            st.session_state.pending_new_values = []
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pending_new_values = []
            st.rerun()


@st.dialog("Confirm Delete Column")
def delete_column_confirmation_dialog(column_name: str):
    """
    Dialog to confirm column deletion.

    Args:
        column_name: Name of the column to delete
    """
    st.write(f"Are you sure you want to delete column **'{column_name}'**?")
    st.warning("This action cannot be undone.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete", type="primary", use_container_width=True):
            try:
                new_df = delete_column(st.session_state.current_df, column_name)
                st.session_state.current_df = new_df
                # Remove from original uniques if present
                if column_name in st.session_state.original_unique_values:
                    del st.session_state.original_unique_values[column_name]
                st.session_state.column_to_delete = None
                st.rerun()
            except KeyError as e:
                st.error(f"Error: {str(e)}")
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.column_to_delete = None
            st.rerun()


@st.dialog("Add New Column")
def add_column_dialog():
    """Dialog to add a new column to the table."""
    st.write("Enter a name for the new column:")

    new_col_name = st.text_input("Column name", key="new_column_name_input")

    if st.button("Add Column", type="primary", use_container_width=True):
        if new_col_name:
            is_valid, msg = validate_column_name(
                st.session_state.current_df,
                new_col_name.strip()
            )
            if is_valid:
                new_df = add_column(
                    st.session_state.current_df,
                    new_col_name.strip(),
                    default_value=""
                )
                st.session_state.current_df = new_df
                st.rerun()
            else:
                st.error(msg)
        else:
            st.error("Please enter a column name.")


@st.dialog("Save As")
def save_as_dialog():
    """Dialog for Save As operation to save to a new filename."""
    st.write("Enter a new filename:")

    new_filename = st.text_input(
        "Filename",
        placeholder="new_file.csv",
        key="save_as_filename_input"
    )

    if st.button("Save", type="primary", use_container_width=True):
        if new_filename:
            success, msg, new_path = workflow.save_file_as(
                st.session_state.working_directory,
                new_filename,
                st.session_state.current_df
            )
            if success:
                st.success(msg)
                # Update current file path and history
                st.session_state.current_file_path = new_path
                st.session_state.file_history = workflow.update_file_history(
                    get_history_path(),
                    new_path
                )
                st.rerun()
            else:
                st.error(msg)
        else:
            st.error("Please enter a filename.")


# =============================================================================
# Sidebar UI
# =============================================================================

def render_sidebar():
    """
    Render the sidebar with:
    - Working directory configuration
    - File selector dropdown
    - Recently opened files
    - Unique value confirmation toggle
    """
    st.sidebar.title("Table Editor")

    # Working directory input
    st.sidebar.subheader("Working Directory")
    working_dir = st.sidebar.text_input(
        "Directory path",
        value=st.session_state.working_directory,
        key="working_dir_input",
        help="Enter the path to a directory containing CSV files"
    )

    # Update working directory if changed
    if working_dir != st.session_state.working_directory:
        if os.path.isdir(working_dir):
            st.session_state.working_directory = working_dir
            # Load history from new directory
            st.session_state.file_history = workflow.load_file_history(
                get_history_path()
            )
        else:
            st.sidebar.error("Invalid directory path")

    # File selector
    st.sidebar.subheader("Select File")
    available_files = workflow.list_available_files(st.session_state.working_directory)

    if available_files:
        file_options = {f['name']: f['path'] for f in available_files}
        selected_file = st.sidebar.selectbox(
            "CSV Files",
            options=list(file_options.keys()),
            key="file_selector"
        )

        if st.sidebar.button("Open File", use_container_width=True):
            if selected_file:
                load_file(file_options[selected_file])
    else:
        st.sidebar.info("No CSV files found in the working directory.")

    # Recently opened files
    with st.sidebar.expander("Recently Opened", expanded=False):
        display_history = workflow.get_display_history(st.session_state.file_history)

        if display_history:
            for entry in display_history[:10]:  # Show last 10 files
                col1, col2 = st.columns([3, 1])
                with col1:
                    file_label = entry['display_name']
                    if not entry['exists']:
                        file_label += " (missing)"
                    st.text(file_label)
                    st.caption(entry['last_opened_display'])
                with col2:
                    if entry['exists']:
                        if st.button("Open", key=f"open_{entry['path']}", use_container_width=True):
                            load_file(entry['path'])
        else:
            st.write("No recently opened files.")

    # Settings section
    st.sidebar.divider()
    st.sidebar.subheader("Settings")

    confirm_toggle = st.sidebar.checkbox(
        "Confirm new values",
        value=st.session_state.confirm_new_values_enabled,
        help="When enabled, prompts for confirmation when entering values not previously in a column"
    )
    st.session_state.confirm_new_values_enabled = confirm_toggle


def load_file(file_path: str):
    """
    Load a CSV file and update session state.

    Args:
        file_path: Absolute path to the CSV file
    """
    try:
        df, metadata = workflow.open_file(file_path)
        st.session_state.current_file_path = file_path
        st.session_state.current_df = df
        st.session_state.original_unique_values = workflow.capture_unique_values(df)

        # Update file history
        st.session_state.file_history = workflow.update_file_history(
            get_history_path(),
            file_path
        )

        st.sidebar.success(f"Loaded: {metadata['name']}")
        st.rerun()
    except FileNotFoundError:
        st.sidebar.error("File not found.")
    except Exception as e:
        st.sidebar.error(f"Error loading file: {str(e)}")


# =============================================================================
# Main Editor Area
# =============================================================================

def render_main_area():
    """
    Render the main area with Editor and Viewer tabs.
    """
    # Header with current file info
    if st.session_state.current_file_path:
        file_name = Path(st.session_state.current_file_path).name
        st.header(f"File: {file_name}")
    else:
        st.header("Table Editor")
        st.info("Select a file from the sidebar to begin editing.")
        return

    if st.session_state.current_df is None:
        st.warning("No data loaded.")
        return

    # Create tabs for Viewer and Editor
    viewer_tab, editor_tab = st.tabs(["Viewer", "Editor"])

    with viewer_tab:
        render_viewer_tab()

    with editor_tab:
        render_editor_tab()


def render_editor_tab():
    """
    Render the Editor tab with:
    - st.data_editor for table editing
    - Action buttons (Add Column, Delete Column, Save, Save As)
    """
    # Configure string columns as text to avoid type inference issues
    # (e.g., email columns getting special validation)
    # Leave numeric columns with default config
    column_config = {}
    for col in st.session_state.current_df.columns:
        if st.session_state.current_df[col].dtype == 'object':
            column_config[col] = st.column_config.TextColumn(col)

    # Data editor widget - always sync back to session state
    # st.data_editor manages its own state via the key
    edited_df = st.data_editor(
        st.session_state.current_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config=column_config,
        key="main_data_editor"
    )

    # Update session state with the editor's current state
    # Don't modify the DataFrame (no reset_index) to avoid re-render issues
    st.session_state.current_df = edited_df

    # Action buttons row
    st.divider()
    render_action_buttons()

    # Check for new unique values if feature is enabled (after buttons, non-blocking)
    if st.session_state.confirm_new_values_enabled and edited_df is not None:
        new_values = workflow.check_for_new_values(
            st.session_state.original_unique_values,
            edited_df
        )
        if new_values:
            st.session_state.pending_new_values = new_values


def render_viewer_tab():
    """
    Render the Viewer tab with:
    - Read-only data display with column sorting
    - Row count info
    """
    st.caption(f"{len(st.session_state.current_df)} rows, {len(st.session_state.current_df.columns)} columns")

    # st.dataframe supports native column sorting when clicked
    st.dataframe(
        st.session_state.current_df,
        use_container_width=True,
        hide_index=False,
        key="main_data_viewer"
    )


def render_action_buttons():
    """Render the action buttons for column operations and saving."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Add Column", use_container_width=True):
            add_column_dialog()

    with col2:
        # Column delete selector and button
        if st.session_state.current_df is not None:
            columns = list(st.session_state.current_df.columns)
            if columns:
                selected_col = st.selectbox(
                    "Column to delete",
                    options=columns,
                    key="delete_column_selector",
                    label_visibility="collapsed"
                )
                if st.button("Delete Column", use_container_width=True):
                    st.session_state.column_to_delete = selected_col

    with col3:
        if st.button("Save", type="primary", use_container_width=True):
            handle_save()

    with col4:
        if st.button("Save As", use_container_width=True):
            save_as_dialog()


def handle_save():
    """Handle the Save button click."""
    if st.session_state.current_file_path and st.session_state.current_df is not None:
        success, msg = workflow.save_file(
            st.session_state.current_file_path,
            st.session_state.current_df
        )
        if success:
            st.success(msg)
            # Update original unique values after save
            st.session_state.original_unique_values = workflow.capture_unique_values(
                st.session_state.current_df
            )
        else:
            st.error(msg)
    else:
        st.warning("No file loaded to save.")


# =============================================================================
# Main Render Function
# =============================================================================

def render_table_editor():
    """
    Main entry point for the Table Editor UI.

    Called by app.py or can be run standalone with:
    streamlit run table_editor_app.py
    """
    initialize_session_state()

    # Load initial file history
    if not st.session_state.file_history:
        st.session_state.file_history = workflow.load_file_history(get_history_path())

    # Render sidebar
    render_sidebar()

    # Render main area with tabs
    render_main_area()

    # Handle pending confirmations
    if st.session_state.pending_new_values:
        new_value_confirmation_dialog(st.session_state.pending_new_values[0])

    if st.session_state.column_to_delete:
        delete_column_confirmation_dialog(st.session_state.column_to_delete)


# =============================================================================
# Standalone Execution
# =============================================================================

if __name__ == "__main__":
    # Run the app standalone with: streamlit run table_editor_app.py
    # Note: st.set_page_config() is called at the top of this file
    render_table_editor()
