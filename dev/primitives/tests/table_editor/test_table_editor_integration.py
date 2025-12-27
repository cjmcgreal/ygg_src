"""
Integration tests for the Table Editor feature.

These tests verify end-to-end workflows that span multiple layers:
- Database layer (table_editor_db.py)
- Logic layer (table_editor_logic.py)
- Workflow layer (table_editor_workflow.py)

Focus: Critical user workflows that require integration between layers.
"""

import os
import json
import shutil
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from table_editor.table_editor_db import CSVDatabase
from table_editor.table_editor_workflow import (
    open_file,
    save_file,
    save_file_as,
    capture_unique_values,
    check_for_new_values,
    update_file_history,
    load_file_history,
    get_display_history
)

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


class TestOpenEditSaveWorkflow:
    """
    Tests for the complete open -> edit -> save workflow.

    Verifies that a user can load a CSV, make changes, and save successfully
    with all layers working together.
    """

    def test_complete_workflow_load_csv_detect_changes_save_file(self):
        """
        Test the complete user workflow: open file, make edits, save changes.

        This integration test verifies:
        1. File loads correctly via workflow layer
        2. Edits are properly tracked
        3. Save persists changes to disk
        4. File can be reloaded with changes intact
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup: Copy fixture to temp directory
            source_csv = FIXTURES_DIR / 'sample_data.csv'
            test_csv = Path(temp_dir) / 'test_data.csv'
            shutil.copy(source_csv, test_csv)

            # Step 1: Open file through workflow
            df, metadata = open_file(str(test_csv))

            # Verify file loaded correctly
            assert len(df) == 5
            assert metadata['name'] == 'test_data.csv'
            assert metadata['exists'] is True

            # Step 2: Make edits (add a new row)
            new_row = pd.DataFrame({
                'id': [6],
                'name': ['Frank'],
                'status': ['active'],
                'category': ['D']
            })
            edited_df = pd.concat([df, new_row], ignore_index=True)

            # Step 3: Save changes through workflow
            success, msg = save_file(str(test_csv), edited_df)

            # Verify save succeeded
            assert success is True
            assert 'successfully' in msg.lower()

            # Step 4: Reload file and verify changes persisted
            reloaded_df, _ = open_file(str(test_csv))

            assert len(reloaded_df) == 6
            assert 'Frank' in reloaded_df['name'].values
            assert 'D' in reloaded_df['category'].values


class TestUniqueValueDetectionEndToEnd:
    """
    Tests for unique value detection across the full workflow.

    Verifies that new values are correctly detected when comparing
    edited data against the original baseline.
    """

    def test_unique_value_detection_through_workflow(self):
        """
        Test unique value detection from file load through edit detection.

        Verifies the complete flow:
        1. Load file and capture baseline unique values
        2. Edit existing row to add new value (not a new row)
        3. Detect new values correctly through workflow layer
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup: Copy fixture to temp directory
            source_csv = FIXTURES_DIR / 'sample_data.csv'
            test_csv = Path(temp_dir) / 'test_data.csv'
            shutil.copy(source_csv, test_csv)

            # Step 1: Load file and capture baseline
            df, _ = open_file(str(test_csv))
            baseline_uniques = capture_unique_values(df)

            # Verify baseline captured correctly
            assert 'status' in baseline_uniques
            assert baseline_uniques['status'] == {'active', 'inactive', 'pending'}

            # Step 2: Edit existing row to change status to a new value
            # This simulates a user editing an existing cell
            edited_df = df.copy()
            edited_df.loc[0, 'status'] = 'suspended'  # Change first row status

            # Step 3: Check for new values through workflow
            new_values = check_for_new_values(baseline_uniques, edited_df)

            # Verify new value detected
            assert len(new_values) == 1
            assert new_values[0]['column'] == 'status'
            assert new_values[0]['value'] == 'suspended'


class TestFileHistoryPersistence:
    """
    Tests for file history persistence across simulated sessions.

    Verifies that file history is correctly saved and loaded,
    simulating multiple user sessions.
    """

    def test_file_history_persistence_across_sessions(self):
        """
        Test that file history persists and is correctly formatted for display.

        Simulates:
        1. First session: Open a file and update history
        2. Second session: Load history and open another file
        3. Verify history contains both files with correct metadata
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup: Copy fixture files
            source_csv1 = FIXTURES_DIR / 'sample_data.csv'
            source_csv2 = FIXTURES_DIR / 'products.csv'
            test_csv1 = Path(temp_dir) / 'data1.csv'
            test_csv2 = Path(temp_dir) / 'data2.csv'
            shutil.copy(source_csv1, test_csv1)
            shutil.copy(source_csv2, test_csv2)

            history_path = str(Path(temp_dir) / '.history.json')

            # Session 1: Open first file and update history
            df1, _ = open_file(str(test_csv1))
            history = update_file_history(history_path, str(test_csv1))

            assert len(history) == 1
            assert history[0]['display_name'] == 'data1.csv'

            # Session 2: Open second file and update history
            df2, _ = open_file(str(test_csv2))
            history = update_file_history(history_path, str(test_csv2))

            assert len(history) == 2

            # Simulate new session: Load history from disk
            loaded_history = load_file_history(history_path)

            # Verify history loaded correctly
            assert len(loaded_history) == 2

            # Get display-ready history
            display_history = get_display_history(loaded_history)

            # Verify display format
            assert len(display_history) == 2
            for entry in display_history:
                assert 'display_name' in entry
                assert 'last_opened_display' in entry
                assert 'exists' in entry
                assert entry['exists'] is True


class TestSaveAsWorkflow:
    """
    Tests for the Save As functionality.

    Verifies that files can be saved to new locations without
    affecting the original file.
    """

    def test_save_as_creates_new_file_preserves_original(self):
        """
        Test Save As creates a new file while preserving the original.

        Verifies:
        1. Original file remains unchanged
        2. New file is created with correct content
        3. Both files are independently accessible
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup: Copy fixture to temp directory
            source_csv = FIXTURES_DIR / 'sample_data.csv'
            original_csv = Path(temp_dir) / 'original.csv'
            shutil.copy(source_csv, original_csv)

            # Load original file
            df, _ = open_file(str(original_csv))
            original_row_count = len(df)

            # Make edits
            new_row = pd.DataFrame({
                'id': [99],
                'name': ['NewPerson'],
                'status': ['new'],
                'category': ['Z']
            })
            edited_df = pd.concat([df, new_row], ignore_index=True)

            # Save As to new file
            success, msg, new_path = save_file_as(temp_dir, 'backup.csv', edited_df)

            # Verify Save As succeeded
            assert success is True
            assert Path(new_path).exists()

            # Verify original file unchanged
            original_df, _ = open_file(str(original_csv))
            assert len(original_df) == original_row_count
            assert 'NewPerson' not in original_df['name'].values

            # Verify new file has changes
            backup_df, _ = open_file(new_path)
            assert len(backup_df) == original_row_count + 1
            assert 'NewPerson' in backup_df['name'].values


class TestMultipleNewValueDetection:
    """
    Tests for detecting multiple new values across different columns.
    """

    def test_detects_new_values_in_multiple_columns(self):
        """
        Test that new value detection works across multiple columns simultaneously.

        Verifies detection of new values added to different columns in a single edit.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            source_csv = FIXTURES_DIR / 'sample_data.csv'
            test_csv = Path(temp_dir) / 'test_data.csv'
            shutil.copy(source_csv, test_csv)

            # Load and capture baseline
            df, _ = open_file(str(test_csv))
            baseline = capture_unique_values(df)

            # Edit: Add row with new values in multiple columns
            new_row = pd.DataFrame({
                'id': [100],
                'name': ['Zoe'],  # New name
                'status': ['archived'],  # New status
                'category': ['X']  # New category
            })
            edited_df = pd.concat([df, new_row], ignore_index=True)

            # Check for new values
            new_values = check_for_new_values(baseline, edited_df)

            # Verify all new values detected
            new_value_tuples = {(v['column'], v['value']) for v in new_values}

            assert ('name', 'Zoe') in new_value_tuples
            assert ('status', 'archived') in new_value_tuples
            assert ('category', 'X') in new_value_tuples


if __name__ == "__main__":
    """Run integration tests using pytest when executed directly."""
    pytest.main([__file__, '-v'])
