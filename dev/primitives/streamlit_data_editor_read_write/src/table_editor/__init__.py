"""
Table Editor module.

A Streamlit-based CSV table editor with database abstraction layer.
"""

from .table_editor_db import (
    CSVDatabase,
    DatabaseInterface,
    load_csv,
    save_csv,
    list_csv_files,
    get_file_info,
    file_exists,
    load_history,
    save_history,
    get_database,
)

__all__ = [
    'CSVDatabase',
    'DatabaseInterface',
    'load_csv',
    'save_csv',
    'list_csv_files',
    'get_file_info',
    'file_exists',
    'load_history',
    'save_history',
    'get_database',
]
