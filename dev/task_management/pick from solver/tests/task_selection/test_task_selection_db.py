"""
Pytest tests for task_selection_db.py

Tests cover CSV database operations for domains, tasks, and solver runs.
Limited to 2-8 focused tests as per project requirements.
"""

import pytest
import pandas as pd
import json
import sys
from pathlib import Path

# Add src directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from task_selection.task_selection_db import (
    load_domains,
    save_domains,
    get_domain_by_name,
    load_tasks,
    save_tasks,
    get_next_task_id,
    get_task_by_id,
    delete_task_by_id,
    load_solver_runs,
    save_solver_run,
    get_solver_run_by_id,
    get_all_solver_runs
)


# ==============================================================================
# TEST 1: Load domains from CSV
# ==============================================================================

def test_load_domains_returns_dataframe():
    """
    Test that load_domains() returns a valid DataFrame with expected columns.

    This verifies that the domains CSV can be read and has the correct schema.
    """
    domains_df = load_domains()

    # Check that we got a DataFrame
    assert isinstance(domains_df, pd.DataFrame), "load_domains() should return a DataFrame"

    # Check that required columns exist
    required_columns = {'id', 'name', 'color'}
    assert required_columns.issubset(domains_df.columns), \
        f"Domains DataFrame should have columns: {required_columns}"

    # Check that we have at least some domains
    assert len(domains_df) > 0, "Domains CSV should contain at least one domain"

    # Check that domain names are strings
    assert domains_df['name'].dtype == 'object', "Domain names should be strings"


# ==============================================================================
# TEST 2: Save and reload domains preserves data integrity
# ==============================================================================

def test_save_domains_preserves_data():
    """
    Test that saving and reloading domains preserves all data correctly.

    This verifies the save/load cycle maintains data integrity.
    """
    # Load original domains
    original_domains_df = load_domains()

    # Save domains back to CSV
    save_result = save_domains(original_domains_df)
    assert save_result == True, "save_domains() should return True on success"

    # Reload domains
    reloaded_domains_df = load_domains()

    # Compare DataFrames
    # Using equals() to check if DataFrames are identical
    pd.testing.assert_frame_equal(
        original_domains_df.reset_index(drop=True),
        reloaded_domains_df.reset_index(drop=True),
        check_dtype=False  # Allow for minor dtype differences
    )


# ==============================================================================
# TEST 3: Load tasks from CSV
# ==============================================================================

def test_load_tasks_returns_valid_dataframe():
    """
    Test that load_tasks() returns a DataFrame with all required fields.

    This verifies the tasks CSV schema is correct and contains expected data.
    """
    tasks_df = load_tasks()

    # Check that we got a DataFrame
    assert isinstance(tasks_df, pd.DataFrame), "load_tasks() should return a DataFrame"

    # Check all required columns exist
    required_columns = {
        'id', 'title', 'description', 'domain',
        'project_parent', 'effort', 'value', 'priority'
    }
    assert required_columns.issubset(tasks_df.columns), \
        f"Tasks DataFrame should have columns: {required_columns}"

    # Check that numeric fields are numeric types
    assert pd.api.types.is_numeric_dtype(tasks_df['effort']), \
        "Effort should be numeric"
    assert pd.api.types.is_numeric_dtype(tasks_df['value']), \
        "Value should be numeric"
    assert pd.api.types.is_numeric_dtype(tasks_df['priority']), \
        "Priority should be numeric"


# ==============================================================================
# TEST 4: Save tasks preserves all fields
# ==============================================================================

def test_save_tasks_preserves_all_fields():
    """
    Test that saving and reloading tasks preserves all fields correctly.

    This is critical for data integrity - no data should be lost in save/load.
    """
    # Load original tasks
    original_tasks_df = load_tasks()

    # Create a modified copy with a new task
    tasks_copy = original_tasks_df.copy()
    next_id = get_next_task_id()

    new_task = pd.DataFrame([{
        'id': next_id,
        'title': 'Test task',
        'description': 'Test description',
        'domain': 'testing',
        'project_parent': 'test_project',
        'effort': 5.0,
        'value': 8.0,
        'priority': 2
    }])

    tasks_with_new = pd.concat([tasks_copy, new_task], ignore_index=True)

    # Save the modified tasks
    save_result = save_tasks(tasks_with_new)
    assert save_result == True, "save_tasks() should return True on success"

    # Reload tasks
    reloaded_tasks_df = load_tasks()

    # Check that the new task is present
    assert len(reloaded_tasks_df) == len(tasks_with_new), \
        "Reloaded tasks should include new task"

    # Verify the new task exists and has correct fields
    new_task_retrieved = reloaded_tasks_df[reloaded_tasks_df['id'] == next_id]
    assert len(new_task_retrieved) == 1, "New task should exist in reloaded data"
    assert new_task_retrieved.iloc[0]['title'] == 'Test task', \
        "New task title should be preserved"

    # Restore original tasks
    save_tasks(original_tasks_df)


# ==============================================================================
# TEST 5: Task CRUD operations work correctly
# ==============================================================================

def test_task_crud_operations():
    """
    Test complete CRUD cycle: get by ID, delete by ID, verify deletion.

    This verifies that individual task operations work correctly.
    """
    # Load original tasks for restoration later
    original_tasks_df = load_tasks()

    # Test get_task_by_id with existing task
    task = get_task_by_id(1)
    assert task is not None, "get_task_by_id(1) should return a task"
    assert task['id'] == 1, "Retrieved task should have ID 1"

    # Test get_task_by_id with non-existent task
    non_existent = get_task_by_id(99999)
    assert non_existent is None, "get_task_by_id with invalid ID should return None"

    # Test delete_task_by_id with existing task
    # Find a task to delete that won't break other tests
    task_to_delete = original_tasks_df.iloc[-1]['id']  # Delete last task
    success, message = delete_task_by_id(task_to_delete)
    assert success == True, f"Deleting task {task_to_delete} should succeed"

    # Verify task is deleted
    deleted_task = get_task_by_id(task_to_delete)
    assert deleted_task is None, "Deleted task should no longer exist"

    # Test delete with non-existent ID
    success, message = delete_task_by_id(99999)
    assert success == False, "Deleting non-existent task should return False"

    # Restore original tasks
    save_tasks(original_tasks_df)


# ==============================================================================
# TEST 6: Solver runs with JSON serialization
# ==============================================================================

def test_solver_run_json_serialization():
    """
    Test that solver runs correctly handle JSON serialization/deserialization.

    This is critical because solver runs store complex data (dicts, lists) as JSON.
    """
    # Create sample solver run data
    sample_run = {
        'available_time': 50.0,
        'algorithm': 'weighted',
        'domain_preferences': {
            'backend': 40,
            'frontend': 35,
            'design': 25
        },
        'selected_tasks': [1, 3, 5, 7],
        'metrics': {
            'total_effort': 18.0,
            'total_value': 30.0,
            'num_tasks': 4
        },
        'explanation': [
            'Selected task 1 with high score',
            'Selected task 3 with good value/effort ratio'
        ]
    }

    # Save the solver run
    success, run_id = save_solver_run(sample_run)
    assert success == True, "save_solver_run should succeed"
    assert run_id is not None, "save_solver_run should return a run ID"

    # Retrieve the solver run
    retrieved_run = get_solver_run_by_id(run_id)
    assert retrieved_run is not None, f"Should be able to retrieve run {run_id}"

    # Verify all fields are correctly deserialized
    assert retrieved_run['algorithm'] == 'weighted', "Algorithm should be preserved"
    assert retrieved_run['available_time'] == 50.0, "Available time should be preserved"

    # Verify JSON fields are correctly parsed back to Python objects
    assert isinstance(retrieved_run['domain_preferences'], dict), \
        "Domain preferences should be a dictionary"
    assert retrieved_run['domain_preferences']['backend'] == 40, \
        "Domain preference values should be preserved"

    assert isinstance(retrieved_run['selected_tasks'], list), \
        "Selected tasks should be a list"
    assert len(retrieved_run['selected_tasks']) == 4, \
        "All selected tasks should be preserved"

    assert isinstance(retrieved_run['metrics'], dict), \
        "Metrics should be a dictionary"
    assert retrieved_run['metrics']['num_tasks'] == 4, \
        "Metric values should be preserved"

    assert isinstance(retrieved_run['explanation'], list), \
        "Explanation should be a list"
    assert len(retrieved_run['explanation']) == 2, \
        "All explanation items should be preserved"


# ==============================================================================
# TEST 7: Get all solver runs sorted by timestamp
# ==============================================================================

def test_get_all_solver_runs_sorted():
    """
    Test that get_all_solver_runs returns runs sorted by timestamp.

    Most recent runs should appear first for easy access.
    """
    # Load all runs
    all_runs_df = get_all_solver_runs()

    # Check that we got a DataFrame
    assert isinstance(all_runs_df, pd.DataFrame), \
        "get_all_solver_runs() should return a DataFrame"

    # If there are multiple runs, verify sorting
    if len(all_runs_df) > 1:
        # Check that timestamps are in descending order
        timestamps = pd.to_datetime(all_runs_df['timestamp'])
        is_sorted_desc = all(timestamps.iloc[i] >= timestamps.iloc[i+1]
                            for i in range(len(timestamps)-1))
        assert is_sorted_desc, "Solver runs should be sorted by timestamp descending"


# ==============================================================================
# TEST 8: Handling of empty/missing data
# ==============================================================================

def test_handling_of_edge_cases():
    """
    Test edge cases like get_next_task_id with varying data states.

    This ensures the system handles edge cases gracefully.
    """
    # Test get_next_task_id returns valid ID
    next_id = get_next_task_id()
    assert isinstance(next_id, int), "get_next_task_id should return an integer"
    assert next_id > 0, "Next task ID should be positive"

    # Verify next_id is greater than all existing IDs
    tasks_df = load_tasks()
    if len(tasks_df) > 0:
        max_existing_id = tasks_df['id'].max()
        assert next_id > max_existing_id, \
            "Next ID should be greater than maximum existing ID"

    # Test get_domain_by_name with non-existent domain
    non_existent_domain = get_domain_by_name('nonexistent_domain_xyz')
    assert non_existent_domain is None, \
        "get_domain_by_name should return None for non-existent domain"

    # Test get_solver_run_by_id with non-existent run
    non_existent_run = get_solver_run_by_id(99999)
    assert non_existent_run is None, \
        "get_solver_run_by_id should return None for non-existent run"
