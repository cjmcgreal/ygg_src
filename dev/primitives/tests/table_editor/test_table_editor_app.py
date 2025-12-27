"""
Tests for Streamlit UI components in table_editor_app.py

Focuses on core functionality that can be tested without a running Streamlit app:
- Session state initialization
- Render function can be imported and called structure is correct
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


class MockSessionState(dict):
    """
    Mock Streamlit session_state that supports both dict and attribute access.

    Streamlit's session_state allows both session_state['key'] and session_state.key
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class TestSessionStateInitialization:
    """Tests for session state initialization."""

    def test_initialize_session_state_creates_expected_variables(self):
        """
        Test that initialize_session_state() creates all required
        session state variables with correct default values.
        """
        mock_session_state = MockSessionState()

        with patch('streamlit.session_state', mock_session_state):
            # Reimport the module to pick up the patched session_state
            import table_editor.table_editor_app as app_module
            importlib.reload(app_module)

            app_module.initialize_session_state()

            # Verify all required state variables are created
            assert 'current_file_path' in mock_session_state
            assert 'current_df' in mock_session_state
            assert 'original_unique_values' in mock_session_state
            assert 'confirm_new_values_enabled' in mock_session_state
            assert 'file_history' in mock_session_state
            assert 'working_directory' in mock_session_state

            # Verify default values
            assert mock_session_state['current_file_path'] is None
            assert mock_session_state['current_df'] is None
            assert mock_session_state['original_unique_values'] == {}
            assert mock_session_state['confirm_new_values_enabled'] is False
            assert mock_session_state['file_history'] == []


class TestRenderTableEditorFunction:
    """Tests for the main render_table_editor() function."""

    def test_render_table_editor_function_exists_and_is_callable(self):
        """
        Test that render_table_editor() function can be imported
        and is callable.
        """
        from table_editor.table_editor_app import render_table_editor

        assert callable(render_table_editor)

    def test_render_table_editor_imports_without_errors(self):
        """
        Test that the table_editor_app module imports successfully
        and exposes expected functions.
        """
        from table_editor import table_editor_app

        # Verify main render function exists
        assert hasattr(table_editor_app, 'render_table_editor')

        # Verify helper functions exist
        assert hasattr(table_editor_app, 'initialize_session_state')
        assert hasattr(table_editor_app, 'render_sidebar')
        assert hasattr(table_editor_app, 'render_editor')
        assert hasattr(table_editor_app, 'render_action_buttons')


class TestSidebarComponents:
    """Tests for sidebar rendering logic."""

    def test_get_history_path_returns_correct_path(self):
        """
        Test that get_history_path() returns the correct path
        for the history JSON file.
        """
        mock_session_state = MockSessionState()
        mock_session_state['working_directory'] = '/test/path'

        with patch('streamlit.session_state', mock_session_state):
            # Reimport to pick up patched session_state
            import table_editor.table_editor_app as app_module
            importlib.reload(app_module)

            result = app_module.get_history_path()

            assert result == '/test/path/.table_editor_history.json'


if __name__ == "__main__":
    """Run tests using pytest when executed directly."""
    pytest.main([__file__, '-v'])
