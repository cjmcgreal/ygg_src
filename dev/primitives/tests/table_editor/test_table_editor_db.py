"""
Tests for the CSVDatabase class in table_editor_db.py

Focuses on core functionality: load, save, list, and file info operations.
"""

import os
import json
import pytest
import pandas as pd
import tempfile
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from table_editor.table_editor_db import CSVDatabase, load_csv, save_csv


class TestCSVDatabaseLoadSave:
    """Tests for CSV load and save operations."""

    def test_load_csv_reads_file_and_returns_dataframe(self):
        """
        Test that load_csv() reads a CSV file and returns a pandas DataFrame
        with the correct data and structure.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test CSV file
            test_path = os.path.join(temp_dir, 'test.csv')
            expected_data = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Alice', 'Bob', 'Charlie'],
                'value': [100, 200, 300]
            })
            expected_data.to_csv(test_path, index=False)

            # Load using CSVDatabase
            db = CSVDatabase()
            result = db.load_csv(test_path)

            # Verify result is a DataFrame with correct shape and values
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 3
            assert list(result.columns) == ['id', 'name', 'value']
            assert result['name'].tolist() == ['Alice', 'Bob', 'Charlie']

    def test_save_csv_writes_dataframe_to_file(self):
        """
        Test that save_csv() writes a DataFrame to a CSV file that can be
        read back with matching data.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db = CSVDatabase()
            test_path = os.path.join(temp_dir, 'output.csv')

            # Create DataFrame and save
            df = pd.DataFrame({
                'col_a': ['x', 'y', 'z'],
                'col_b': [10, 20, 30]
            })
            result = db.save_csv(test_path, df)

            # Verify save was successful
            assert result is True
            assert os.path.exists(test_path)

            # Verify file contents by reading it back
            loaded = pd.read_csv(test_path)
            assert len(loaded) == 3
            assert loaded['col_a'].tolist() == ['x', 'y', 'z']


class TestCSVDatabaseFileOperations:
    """Tests for file listing and info operations."""

    def test_list_csv_files_returns_csv_files_in_directory(self):
        """
        Test that list_csv_files() returns a list of CSV files in a directory,
        excluding non-CSV files.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db = CSVDatabase()

            # Create multiple files (CSV and non-CSV)
            sample_df = pd.DataFrame({'a': [1, 2]})
            db.save_csv(os.path.join(temp_dir, 'file1.csv'), sample_df)
            db.save_csv(os.path.join(temp_dir, 'file2.csv'), sample_df)

            # Create a non-CSV file
            with open(os.path.join(temp_dir, 'notes.txt'), 'w') as f:
                f.write("not a csv")

            # List CSV files
            result = db.list_csv_files(temp_dir)

            # Should find exactly 2 CSV files
            assert len(result) == 2
            assert all('.csv' in path for path in result)
            assert any('file1.csv' in path for path in result)
            assert any('file2.csv' in path for path in result)

    def test_get_file_info_returns_metadata(self):
        """
        Test that get_file_info() returns file metadata including
        name, path, modified timestamp, size, and exists flag.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db = CSVDatabase()

            # Create a test CSV file
            test_path = os.path.join(temp_dir, 'metadata_test.csv')
            df = pd.DataFrame({'data': [1, 2, 3, 4, 5]})
            db.save_csv(test_path, df)

            # Get file info
            info = db.get_file_info(test_path)

            # Verify all expected fields are present
            assert info['name'] == 'metadata_test.csv'
            assert info['exists'] is True
            assert info['size'] > 0
            assert info['modified'] is not None
            assert 'path' in info

            # Verify modified is a valid ISO format timestamp
            datetime.fromisoformat(info['modified'])


class TestCSVDatabaseHistory:
    """Tests for file history persistence."""

    def test_history_save_and_load_roundtrip(self):
        """
        Test that save_history() and load_history() correctly persist
        and retrieve file history data.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            db = CSVDatabase()
            history_path = os.path.join(temp_dir, 'history.json')

            # Create test history data
            test_history = [
                {
                    'path': '/path/to/file1.csv',
                    'last_opened': '2025-12-27T10:30:00',
                    'display_name': 'file1.csv'
                },
                {
                    'path': '/path/to/file2.csv',
                    'last_opened': '2025-12-27T11:00:00',
                    'display_name': 'file2.csv'
                }
            ]

            # Save history
            save_result = db.save_history(history_path, test_history)
            assert save_result is True

            # Load history back
            loaded = db.load_history(history_path)

            # Verify roundtrip integrity
            assert len(loaded) == 2
            assert loaded[0]['path'] == '/path/to/file1.csv'
            assert loaded[1]['display_name'] == 'file2.csv'


if __name__ == "__main__":
    """Run tests using pytest when executed directly."""
    pytest.main([__file__, '-v'])
