"""
Tests for business logic functions in table_editor_logic.py

Focuses on core functionality: unique value tracking and column operations.
"""

import pytest
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from table_editor.table_editor_logic import (
    get_unique_values,
    find_new_values,
    add_column,
    delete_column
)


class TestUniqueValueTracking:
    """Tests for unique value detection and tracking."""

    def test_get_unique_values_extracts_unique_values_per_column(self):
        """
        Test that get_unique_values() extracts unique values for each column
        and returns them as a dictionary of sets.
        """
        # Create test DataFrame with duplicate values
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Alice', 'Charlie'],
            'status': ['active', 'inactive', 'active', 'active'],
            'score': [100, 200, 100, 300]
        })

        result = get_unique_values(df)

        # Verify structure is dict of sets
        assert isinstance(result, dict)
        assert set(result.keys()) == {'name', 'status', 'score'}

        # Verify unique values are extracted correctly
        assert result['name'] == {'Alice', 'Bob', 'Charlie'}
        assert result['status'] == {'active', 'inactive'}
        assert result['score'] == {100, 200, 300}

    def test_find_new_values_identifies_new_values_vs_original(self):
        """
        Test that find_new_values() correctly identifies values that
        exist in the edited DataFrame but not in the original unique values.
        """
        # Original unique values (simulating what was captured at file load)
        original_uniques = {
            'name': {'Alice', 'Bob'},
            'status': {'active', 'inactive'}
        }

        # Edited DataFrame with new values added
        edited_df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],  # 'Charlie' is new
            'status': ['active', 'pending', 'inactive']  # 'pending' is new
        })

        result = find_new_values(original_uniques, edited_df)

        # Result should be a list of dicts with column and value
        assert isinstance(result, list)
        assert len(result) == 2

        # Check that both new values are found
        new_items = {(item['column'], item['value']) for item in result}
        assert ('name', 'Charlie') in new_items
        assert ('status', 'pending') in new_items


class TestColumnOperations:
    """Tests for column add and delete operations."""

    def test_add_column_adds_empty_text_column_to_dataframe(self):
        """
        Test that add_column() adds a new column with the specified name
        and default value to the DataFrame.
        """
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C']
        })

        result = add_column(df, 'description', default_value='')

        # Verify new column exists
        assert 'description' in result.columns
        assert list(result.columns) == ['id', 'name', 'description']

        # Verify all values in new column are the default
        assert result['description'].tolist() == ['', '', '']

        # Verify original DataFrame not modified
        assert 'description' not in df.columns

    def test_delete_column_removes_column_from_dataframe(self):
        """
        Test that delete_column() removes the specified column from
        the DataFrame and returns the modified DataFrame.
        """
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'to_delete': ['x', 'y', 'z']
        })

        result = delete_column(df, 'to_delete')

        # Verify column is removed
        assert 'to_delete' not in result.columns
        assert list(result.columns) == ['id', 'name']

        # Verify other columns still have data
        assert result['id'].tolist() == [1, 2, 3]

        # Verify original DataFrame not modified
        assert 'to_delete' in df.columns


if __name__ == "__main__":
    """Run tests using pytest when executed directly."""
    pytest.main([__file__, '-v'])
