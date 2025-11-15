"""
Pytest Tests for Task Selection Workflow Layer

Tests the orchestration functions that coordinate between UI, database,
logic, and analysis layers.
"""

import pytest
import pandas as pd
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'task_selection'))

from task_selection_workflow import (
    create_task,
    update_task,
    delete_task,
    get_all_tasks,
    get_all_domains,
    get_domain_names,
    run_solver,
    save_solver_run,
    get_solver_run_history,
    get_solver_run_details
)


# ==============================================================================
# TASK CRUD TESTS
# ==============================================================================

def test_create_task_success():
    """Test successful task creation with valid data."""
    success, msg, task_id = create_task(
        title="Test task",
        description="Test description",
        domain="backend",
        project_parent="test_project",
        effort=5.0,
        value=8.0,
        priority=1
    )

    assert success is True
    assert "successfully" in msg.lower()
    assert task_id is not None
    assert isinstance(task_id, int)

    # Cleanup: delete the created task
    delete_task(task_id)


def test_create_task_validation_error():
    """Test task creation fails with invalid data (empty title)."""
    success, msg, task_id = create_task(
        title="",  # Empty title should fail
        description="Test",
        domain="backend",
        project_parent="",
        effort=5.0,
        value=8.0,
        priority=1
    )

    assert success is False
    assert "validation" in msg.lower()
    assert task_id is None


def test_create_task_invalid_domain():
    """Test task creation fails with non-existent domain."""
    success, msg, task_id = create_task(
        title="Test task",
        description="Test",
        domain="nonexistent_domain",
        project_parent="",
        effort=5.0,
        value=8.0,
        priority=1
    )

    assert success is False
    assert "domain" in msg.lower()
    assert task_id is None


def test_update_task_success():
    """Test successful task update."""
    # First create a task
    success, msg, task_id = create_task(
        title="Task to update",
        description="Original",
        domain="backend",
        project_parent="",
        effort=5.0,
        value=8.0,
        priority=1
    )
    assert success is True

    # Update the task
    update_success, update_msg = update_task(
        task_id,
        effort=10.0,
        priority=2
    )

    assert update_success is True
    assert "successfully" in update_msg.lower()

    # Cleanup
    delete_task(task_id)


def test_delete_task_success():
    """Test successful task deletion."""
    # First create a task
    success, msg, task_id = create_task(
        title="Task to delete",
        description="Will be deleted",
        domain="backend",
        project_parent="",
        effort=3.0,
        value=5.0,
        priority=1
    )
    assert success is True

    # Delete the task
    delete_success, delete_msg = delete_task(task_id)

    assert delete_success is True
    assert "deleted" in delete_msg.lower() or "success" in delete_msg.lower()


def test_get_all_tasks():
    """Test retrieving all tasks returns a DataFrame."""
    tasks_df = get_all_tasks()

    assert isinstance(tasks_df, pd.DataFrame)
    # Check for required columns
    required_columns = ['id', 'title', 'domain', 'effort', 'value', 'priority']
    for col in required_columns:
        assert col in tasks_df.columns


# ==============================================================================
# DOMAIN TESTS
# ==============================================================================

def test_get_all_domains():
    """Test retrieving all domains returns a DataFrame."""
    domains_df = get_all_domains()

    assert isinstance(domains_df, pd.DataFrame)
    assert 'name' in domains_df.columns
    assert 'color' in domains_df.columns
    assert len(domains_df) > 0  # Should have sample domains


def test_get_domain_names():
    """Test retrieving domain names returns a list."""
    domain_names = get_domain_names()

    assert isinstance(domain_names, list)
    assert len(domain_names) > 0
    # Check that all items are strings
    assert all(isinstance(name, str) for name in domain_names)


# ==============================================================================
# SOLVER ORCHESTRATION TESTS
# ==============================================================================

def test_run_solver_greedy_success():
    """Test running greedy solver successfully."""
    domain_prefs = {
        'backend': 50,
        'frontend': 30,
        'design': 10,
        'devops': 5,
        'testing': 5
    }

    selected, explanation, metrics, error = run_solver(
        available_time=20.0,
        domain_preferences=domain_prefs,
        algorithm='greedy'
    )

    assert error is None
    assert isinstance(selected, pd.DataFrame)
    assert isinstance(explanation, list)
    assert isinstance(metrics, dict)
    assert 'total_effort' in metrics
    assert 'total_value' in metrics
    assert 'num_tasks' in metrics


def test_run_solver_invalid_bandwidth():
    """Test solver fails with invalid bandwidth allocation (doesn't sum to 100%)."""
    invalid_prefs = {
        'backend': 40,
        'frontend': 50  # Sum = 90, not 100
    }

    selected, explanation, metrics, error = run_solver(
        available_time=20.0,
        domain_preferences=invalid_prefs,
        algorithm='greedy'
    )

    assert error is not None
    assert "bandwidth" in error.lower() or "100" in error


def test_run_solver_invalid_algorithm():
    """Test solver fails with invalid algorithm name."""
    domain_prefs = {
        'backend': 50,
        'frontend': 50
    }

    selected, explanation, metrics, error = run_solver(
        available_time=20.0,
        domain_preferences=domain_prefs,
        algorithm='invalid_algorithm'
    )

    assert error is not None
    assert "algorithm" in error.lower() or "invalid" in error.lower()


def test_solver_run_history():
    """Test retrieving solver run history."""
    # First run a solver
    domain_prefs = {
        'backend': 50,
        'frontend': 30,
        'design': 10,
        'devops': 5,
        'testing': 5
    }

    selected, explanation, metrics, error = run_solver(
        available_time=15.0,
        domain_preferences=domain_prefs,
        algorithm='weighted'
    )

    if error is None and len(selected) > 0:
        # Save the run
        task_ids = selected['id'].tolist()
        save_success, run_id = save_solver_run(
            available_time=15.0,
            domain_preferences=domain_prefs,
            algorithm='weighted',
            selected_task_ids=task_ids,
            metrics=metrics,
            explanation=explanation
        )

        assert save_success is True
        assert run_id is not None

        # Get history
        history_df = get_solver_run_history()
        assert isinstance(history_df, pd.DataFrame)
        assert len(history_df) > 0

        # Get details of the saved run
        run_details = get_solver_run_details(run_id)
        assert run_details is not None
        assert run_details['id'] == run_id
        assert run_details['algorithm'] == 'weighted'
        assert isinstance(run_details['domain_preferences'], dict)
        assert isinstance(run_details['selected_tasks'], list)
