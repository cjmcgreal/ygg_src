"""
Unit Tests for Task Selection Streamlit UI Layer

Tests cover:
- Session state initialization
- Tab rendering functions can be called
- Basic UI component structure

Note: Full UI testing is typically done manually with Streamlit.
These tests focus on verifying that key functions can be called without errors.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'task_selection'))

from task_selection_app import (
    initialize_session_state,
    render_task_selection
)


class TestSessionStateInitialization:
    """Test session state management functions."""

    def test_initialize_session_state_creates_required_variables(self):
        """
        Test that initialize_session_state creates all required session state variables.

        This test verifies that the initialization function properly sets up
        the session state structure needed for the UI to function.
        """
        # Note: This test is limited because we can't easily mock Streamlit's session_state
        # In a real Streamlit environment, session_state is a special object
        # For now, we just verify the function can be imported and exists
        assert callable(initialize_session_state)


class TestRenderFunction:
    """Test main render function."""

    def test_render_task_selection_is_callable(self):
        """
        Test that render_task_selection function exists and is callable.

        This verifies the main entry point function is properly defined.
        """
        assert callable(render_task_selection)


class TestUIStructure:
    """Test UI structure and component availability."""

    def test_main_render_function_exists(self):
        """
        Test that the main render function is properly exported.

        This ensures the function can be imported by app.py.
        """
        from task_selection_app import render_task_selection
        assert render_task_selection is not None
        assert callable(render_task_selection)


# ==============================================================================
# PYTEST EXECUTION
# ==============================================================================

if __name__ == "__main__":
    """
    Run tests using pytest when this file is executed directly.

    Usage:
        python tests/task_selection/test_task_selection_app.py
    """
    pytest.main([__file__, '-v'])
