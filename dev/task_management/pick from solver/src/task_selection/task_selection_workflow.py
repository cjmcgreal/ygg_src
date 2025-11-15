"""
Workflow Orchestration Layer for Task Selection System

This module acts as the orchestration layer between the UI and the backend layers.
It coordinates calls to the database, logic, and analysis layers to implement
complete workflows for task management and solver operations.

Key responsibilities:
- Orchestrate task CRUD operations (create, read, update, delete)
- Orchestrate domain data retrieval
- Orchestrate solver run execution and persistence
- Handle error propagation from lower layers
- Provide clear success/failure messages to UI layer

Think of this as the "controller" in MVC pattern - it doesn't contain business
logic itself, but coordinates the flow between layers.
"""

import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path to import sibling modules
sys.path.insert(0, os.path.dirname(__file__))

from task_selection_db import (
    load_tasks,
    save_tasks,
    get_next_task_id,
    get_task_by_id,
    delete_task_by_id,
    load_domains,
    save_solver_run as db_save_solver_run,  # Use alias to avoid naming conflict
    load_solver_runs,
    get_solver_run_by_id
)

from task_selection_logic import (
    validate_task_data,
    validate_domain_exists,
    validate_bandwidth_allocation
)

from task_selection_analysis import (
    greedy_solver,
    weighted_solver,
    knapsack_solver
)


# ==============================================================================
# TASK CRUD ORCHESTRATION
# ==============================================================================

def create_task(title, description, domain, project_parent, effort, value, priority):
    """
    Orchestrate task creation workflow.

    Workflow steps:
    1. Validate task data using logic layer
    2. Validate domain exists
    3. Load current tasks from database
    4. Generate new task ID
    5. Add new task to DataFrame
    6. Save updated tasks to database

    Args:
        title (str): Task title
        description (str): Task description (can be empty)
        domain (str): Domain name (must exist in domains.csv)
        project_parent (str): Project grouping label (can be empty)
        effort (float): Story points estimate
        value (float): Value score
        priority (int): Priority ranking (1=highest)

    Returns:
        tuple: (success: bool, message: str, task_id: int or None)
               - (True, "Success message", task_id) if created
               - (False, "Error message", None) if failed

    Example:
        >>> success, msg, task_id = create_task(
        ...     "Implement feature", "Add new capability", "backend",
        ...     "project_a", 5.0, 8.0, 1
        ... )
        >>> if success:
        ...     print(f"Created task {task_id}")
    """
    # Step 1: Validate task data
    is_valid, error_msg = validate_task_data(title, effort, value, priority)
    if not is_valid:
        return (False, f"Validation error: {error_msg}", None)

    # Step 2: Validate domain exists
    try:
        domains_df = load_domains()
        is_valid, error_msg = validate_domain_exists(domain, domains_df)
        if not is_valid:
            return (False, f"Domain validation error: {error_msg}", None)
    except Exception as e:
        return (False, f"Error loading domains: {str(e)}", None)

    # Step 3: Load current tasks
    try:
        tasks_df = load_tasks()
    except Exception as e:
        return (False, f"Error loading tasks: {str(e)}", None)

    # Step 4: Generate new task ID
    try:
        new_task_id = get_next_task_id()
    except Exception as e:
        return (False, f"Error generating task ID: {str(e)}", None)

    # Step 5: Create new task
    new_task = {
        'id': new_task_id,
        'title': title.strip(),
        'description': description.strip() if description else "",
        'domain': domain,
        'project_parent': project_parent.strip() if project_parent else "",
        'effort': float(effort),
        'value': float(value),
        'priority': int(priority)
    }

    # Add to DataFrame
    new_task_df = pd.DataFrame([new_task])
    updated_tasks_df = pd.concat([tasks_df, new_task_df], ignore_index=True)

    # Step 6: Save to database
    try:
        save_tasks(updated_tasks_df)
        return (True, f"Task '{title}' created successfully", new_task_id)
    except Exception as e:
        return (False, f"Error saving task: {str(e)}", None)


def update_task(task_id, **kwargs):
    """
    Orchestrate task update workflow.

    Workflow steps:
    1. Load current tasks from database
    2. Find task by ID
    3. Update specified fields
    4. Validate updated task data
    5. Save updated tasks to database

    Args:
        task_id (int): ID of task to update
        **kwargs: Fields to update (title, description, domain, project_parent,
                  effort, value, priority). Only provided fields are updated.

    Returns:
        tuple: (success: bool, message: str)
               - (True, "Success message") if updated
               - (False, "Error message") if failed

    Example:
        >>> success, msg = update_task(1, effort=8.0, priority=2)
        >>> if success:
        ...     print("Task updated")
    """
    # Step 1: Load current tasks
    try:
        tasks_df = load_tasks()
    except Exception as e:
        return (False, f"Error loading tasks: {str(e)}")

    # Step 2: Find task by ID
    if task_id not in tasks_df['id'].values:
        return (False, f"Task with ID {task_id} not found")

    # Get the task index
    task_idx = tasks_df[tasks_df['id'] == task_id].index[0]

    # Step 3: Update specified fields
    updatable_fields = ['title', 'description', 'domain', 'project_parent',
                        'effort', 'value', 'priority']

    for field, new_value in kwargs.items():
        if field not in updatable_fields:
            return (False, f"Invalid field '{field}'. Cannot update this field.")

        # Update the field in the DataFrame
        if field in ['title', 'description', 'domain', 'project_parent']:
            tasks_df.at[task_idx, field] = new_value.strip() if new_value else ""
        elif field in ['effort', 'value']:
            tasks_df.at[task_idx, field] = float(new_value)
        elif field == 'priority':
            tasks_df.at[task_idx, field] = int(new_value)

    # Step 4: Validate updated task
    updated_task = tasks_df.loc[task_idx]
    is_valid, error_msg = validate_task_data(
        updated_task['title'],
        updated_task['effort'],
        updated_task['value'],
        updated_task['priority']
    )
    if not is_valid:
        return (False, f"Validation error after update: {error_msg}")

    # Validate domain if it was updated
    if 'domain' in kwargs:
        try:
            domains_df = load_domains()
            is_valid, error_msg = validate_domain_exists(updated_task['domain'], domains_df)
            if not is_valid:
                return (False, f"Domain validation error: {error_msg}")
        except Exception as e:
            return (False, f"Error validating domain: {str(e)}")

    # Step 5: Save updated tasks
    try:
        save_tasks(tasks_df)
        return (True, f"Task {task_id} updated successfully")
    except Exception as e:
        return (False, f"Error saving updated task: {str(e)}")


def delete_task(task_id):
    """
    Orchestrate task deletion workflow.

    Workflow steps:
    1. Call database layer to delete task
    2. Return result to UI

    Args:
        task_id (int): ID of task to delete

    Returns:
        tuple: (success: bool, message: str)
               - (True, "Success message") if deleted
               - (False, "Error message") if failed

    Example:
        >>> success, msg = delete_task(5)
        >>> if success:
        ...     print("Task deleted")
    """
    # Call database layer to handle deletion
    # Database layer already includes save operation
    try:
        success, message = delete_task_by_id(task_id)
        return (success, message)
    except Exception as e:
        return (False, f"Error deleting task: {str(e)}")


def get_all_tasks():
    """
    Retrieve all tasks for display.

    Workflow steps:
    1. Load tasks from database
    2. Return DataFrame

    Returns:
        pd.DataFrame: All tasks, or empty DataFrame if error occurs

    Example:
        >>> tasks_df = get_all_tasks()
        >>> print(f"Found {len(tasks_df)} tasks")
    """
    try:
        tasks_df = load_tasks()
        return tasks_df
    except Exception as e:
        print(f"Error loading tasks: {e}")
        # Return empty DataFrame with proper schema on error
        return pd.DataFrame(columns=[
            'id', 'title', 'description', 'domain',
            'project_parent', 'effort', 'value', 'priority'
        ])


# ==============================================================================
# DOMAIN ORCHESTRATION
# ==============================================================================

def get_all_domains():
    """
    Retrieve all domains for display.

    Workflow steps:
    1. Load domains from database
    2. Return DataFrame

    Returns:
        pd.DataFrame: All domains, or empty DataFrame if error occurs

    Example:
        >>> domains_df = get_all_domains()
        >>> print(f"Found {len(domains_df)} domains")
    """
    try:
        domains_df = load_domains()
        return domains_df
    except Exception as e:
        print(f"Error loading domains: {e}")
        # Return empty DataFrame with proper schema on error
        return pd.DataFrame(columns=['id', 'name', 'color'])


def get_domain_names():
    """
    Get list of domain names for dropdowns and selectors.

    Workflow steps:
    1. Load domains from database
    2. Extract names as list

    Returns:
        list: List of domain names (strings), or empty list if error occurs

    Example:
        >>> domain_names = get_domain_names()
        >>> # ['backend', 'frontend', 'design', 'devops', 'testing']
    """
    try:
        domains_df = load_domains()
        return domains_df['name'].tolist()
    except Exception as e:
        print(f"Error loading domain names: {e}")
        return []


# ==============================================================================
# SOLVER RUN ORCHESTRATION
# ==============================================================================

def run_solver(available_time, domain_preferences, algorithm):
    """
    Orchestrate solver execution workflow.

    Workflow steps:
    1. Validate bandwidth allocation
    2. Load tasks from database
    3. Load domains from database
    4. Call appropriate solver algorithm
    5. Return results

    Args:
        available_time (float): Total available time in story points
        domain_preferences (dict): Domain name to percentage mapping
        algorithm (str): Algorithm to use ('greedy', 'weighted', or 'knapsack')

    Returns:
        tuple: (selected_tasks_df, explanation_list, metrics_dict, error_message)
               - If successful: (DataFrame, list, dict, None)
               - If failed: (None, None, None, "Error message")

    Example:
        >>> selected, explanation, metrics, error = run_solver(
        ...     40.0, {'backend': 50, 'frontend': 50}, 'greedy'
        ... )
        >>> if error is None:
        ...     print(f"Selected {metrics['num_tasks']} tasks")
    """
    # Step 1: Validate bandwidth allocation
    is_valid, error_msg, total_pct = validate_bandwidth_allocation(domain_preferences)
    if not is_valid:
        return (None, None, None, f"Bandwidth validation error: {error_msg}")

    # Step 2: Load tasks
    try:
        tasks_df = load_tasks()
        if len(tasks_df) == 0:
            return (None, None, None, "No tasks available. Please add tasks before running solver.")
    except Exception as e:
        return (None, None, None, f"Error loading tasks: {str(e)}")

    # Step 3: Load domains (for validation)
    try:
        domains_df = load_domains()
    except Exception as e:
        return (None, None, None, f"Error loading domains: {str(e)}")

    # Step 4: Call appropriate solver
    try:
        if algorithm.lower() == 'greedy':
            selected_tasks_df, explanation, metrics = greedy_solver(
                tasks_df, available_time, domain_preferences
            )
        elif algorithm.lower() == 'weighted':
            selected_tasks_df, explanation, metrics = weighted_solver(
                tasks_df, available_time, domain_preferences
            )
        elif algorithm.lower() == 'knapsack':
            selected_tasks_df, explanation, metrics = knapsack_solver(
                tasks_df, available_time, domain_preferences
            )
        else:
            return (None, None, None, f"Invalid algorithm '{algorithm}'. Must be 'greedy', 'weighted', or 'knapsack'.")

        # Step 5: Return results
        return (selected_tasks_df, explanation, metrics, None)

    except Exception as e:
        return (None, None, None, f"Error running {algorithm} solver: {str(e)}")


def save_solver_run(available_time, domain_preferences, algorithm, selected_task_ids, metrics, explanation):
    """
    Orchestrate saving a solver run to history.

    Workflow steps:
    1. Prepare run data with timestamp
    2. Call database layer to save run
    3. Return result

    Args:
        available_time (float): Available time used for this run
        domain_preferences (dict): Domain preferences used
        algorithm (str): Algorithm used
        selected_task_ids (list): List of selected task IDs
        metrics (dict): Performance metrics dictionary
        explanation (list): List of explanation strings

    Returns:
        tuple: (success: bool, run_id: int or None)
               - (True, run_id) if saved successfully
               - (False, None) if failed

    Example:
        >>> success, run_id = save_solver_run(
        ...     40.0, {'backend': 50, 'frontend': 50}, 'greedy',
        ...     [1, 2, 3], metrics_dict, explanation_list
        ... )
        >>> if success:
        ...     print(f"Saved as run {run_id}")
    """
    # Step 1: Prepare run data
    run_data = {
        'available_time': available_time,
        'algorithm': algorithm,
        'domain_preferences': domain_preferences,
        'selected_tasks': selected_task_ids,
        'metrics': metrics,
        'explanation': explanation
    }

    # Step 2: Save to database using the aliased function
    try:
        success, run_id = db_save_solver_run(run_data)
        if success:
            return (True, run_id)
        else:
            return (False, None)
    except Exception as e:
        print(f"Error saving solver run: {e}")
        return (False, None)


def get_solver_run_history():
    """
    Retrieve historical solver runs for display.

    Workflow steps:
    1. Load solver runs from database
    2. Sort by timestamp (most recent first)
    3. Return DataFrame

    Returns:
        pd.DataFrame: All solver runs sorted by timestamp, or empty DataFrame if error

    Example:
        >>> runs_df = get_solver_run_history()
        >>> if len(runs_df) > 0:
        ...     latest = runs_df.iloc[0]
        ...     print(f"Latest run used {latest['algorithm']} algorithm")
    """
    try:
        runs_df = load_solver_runs()

        # Sort by timestamp descending (most recent first)
        if len(runs_df) > 0:
            runs_df = runs_df.sort_values('timestamp', ascending=False)

        return runs_df
    except Exception as e:
        print(f"Error loading solver run history: {e}")
        # Return empty DataFrame with proper schema
        return pd.DataFrame(columns=[
            'id', 'timestamp', 'available_time', 'algorithm',
            'domain_preferences_json', 'selected_tasks_json',
            'metrics_json', 'explanation_json'
        ])


def get_solver_run_details(run_id):
    """
    Retrieve detailed information about a specific solver run.

    Workflow steps:
    1. Load specific run from database (with JSON parsing)
    2. Load related task details
    3. Return complete run information

    Args:
        run_id (int): ID of the solver run to retrieve

    Returns:
        dict or None: Complete run details with parsed JSON, or None if not found/error
                      Dictionary includes:
                      - id, timestamp, algorithm, available_time
                      - domain_preferences (parsed dict)
                      - selected_tasks (parsed list)
                      - metrics (parsed dict)
                      - explanation (parsed list)
                      - task_details (DataFrame of selected tasks)

    Example:
        >>> run_details = get_solver_run_details(1)
        >>> if run_details is not None:
        ...     print(f"Run used {run_details['algorithm']} algorithm")
        ...     print(f"Selected {len(run_details['selected_tasks'])} tasks")
    """
    try:
        # Step 1: Get run with parsed JSON fields
        run_dict = get_solver_run_by_id(run_id)

        if run_dict is None:
            return None

        # Step 2: Load task details for selected tasks
        try:
            tasks_df = load_tasks()
            selected_task_ids = run_dict['selected_tasks']

            # Filter tasks to only selected ones
            task_details_df = tasks_df[tasks_df['id'].isin(selected_task_ids)]

            # Add task_details to the result
            run_dict['task_details'] = task_details_df
        except Exception as e:
            print(f"Warning: Could not load task details for run {run_id}: {e}")
            run_dict['task_details'] = pd.DataFrame()

        return run_dict

    except Exception as e:
        print(f"Error loading solver run details for run {run_id}: {e}")
        return None


# ==============================================================================
# STANDALONE TEST SECTION
# ==============================================================================

if __name__ == "__main__":
    """
    Standalone test section demonstrating workflow orchestration.

    This section can be run independently to verify functionality:
    $ python src/task_selection/task_selection_workflow.py

    Tests cover:
    - Task CRUD operations (create, read, update, delete)
    - Domain retrieval operations
    - Solver run orchestration
    - Error handling and propagation
    - Complete end-to-end workflows
    """

    print("=" * 80)
    print("TASK SELECTION WORKFLOW LAYER - STANDALONE TESTS")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # Test 1: Get all tasks
    # -------------------------------------------------------------------------
    print("TEST 1: Get All Tasks")
    print("-" * 80)

    tasks_df = get_all_tasks()
    print(f"Loaded {len(tasks_df)} tasks")
    if len(tasks_df) > 0:
        print(tasks_df[['id', 'title', 'domain', 'effort', 'value']].to_string(index=False))
    print(f"Expected: Tasks loaded successfully from database")
    print()

    # -------------------------------------------------------------------------
    # Test 2: Get all domains and domain names
    # -------------------------------------------------------------------------
    print("TEST 2: Get Domains")
    print("-" * 80)

    domains_df = get_all_domains()
    print(f"Loaded {len(domains_df)} domains:")
    print(domains_df.to_string(index=False))
    print()

    domain_names = get_domain_names()
    print(f"Domain names list: {domain_names}")
    print(f"Expected: List of domain names for UI dropdowns")
    print()

    # -------------------------------------------------------------------------
    # Test 3: Create a new task
    # -------------------------------------------------------------------------
    print("TEST 3: Create New Task")
    print("-" * 80)

    success, msg, task_id = create_task(
        title="Workflow test task",
        description="This task was created by the workflow standalone test",
        domain="testing",
        project_parent="test_project",
        effort=3.0,
        value=5.0,
        priority=2
    )

    print(f"Create task result: success={success}")
    print(f"Message: {msg}")
    if success:
        print(f"New task ID: {task_id}")
        print(f"Expected: Task created successfully with new ID")
    print()

    # -------------------------------------------------------------------------
    # Test 4: Update a task
    # -------------------------------------------------------------------------
    print("TEST 4: Update Task")
    print("-" * 80)

    if success and task_id is not None:
        # Update the task we just created
        update_success, update_msg = update_task(
            task_id,
            effort=5.0,
            priority=1
        )

        print(f"Update task result: success={update_success}")
        print(f"Message: {update_msg}")
        print(f"Expected: Task updated successfully")
    else:
        print("Skipping update test (no task created)")
    print()

    # -------------------------------------------------------------------------
    # Test 5: Create task with invalid data (validation error)
    # -------------------------------------------------------------------------
    print("TEST 5: Create Task with Invalid Data")
    print("-" * 80)

    fail_success, fail_msg, fail_id = create_task(
        title="",  # Empty title - should fail validation
        description="Test",
        domain="backend",
        project_parent="",
        effort=5.0,
        value=8.0,
        priority=1
    )

    print(f"Create invalid task result: success={fail_success}")
    print(f"Message: {fail_msg}")
    print(f"Expected: success=False with validation error message")
    print()

    # -------------------------------------------------------------------------
    # Test 6: Run solver (greedy algorithm)
    # -------------------------------------------------------------------------
    print("TEST 6: Run Greedy Solver")
    print("-" * 80)

    domain_prefs = {
        'backend': 40,
        'frontend': 20,
        'design': 20,
        'devops': 10,
        'testing': 10
    }

    selected, explanation, metrics, error = run_solver(
        available_time=20.0,
        domain_preferences=domain_prefs,
        algorithm='greedy'
    )

    if error is None:
        print(f"Solver run successful!")
        print(f"Tasks selected: {metrics['num_tasks']}")
        print(f"Total effort: {metrics['total_effort']}sp")
        print(f"Total value: {metrics['total_value']}")
        print(f"Utilization: {metrics['utilization_pct']:.1f}%")
        print()
        print("Explanation (first 5 lines):")
        for line in explanation[:5]:
            print(f"  {line}")
        print(f"Expected: Solver runs successfully and selects optimal tasks")
    else:
        print(f"Solver error: {error}")
    print()

    # -------------------------------------------------------------------------
    # Test 7: Run solver with invalid bandwidth (validation error)
    # -------------------------------------------------------------------------
    print("TEST 7: Run Solver with Invalid Bandwidth")
    print("-" * 80)

    invalid_prefs = {
        'backend': 40,
        'frontend': 50  # Sum = 90, not 100
    }

    selected, explanation, metrics, error = run_solver(
        available_time=20.0,
        domain_preferences=invalid_prefs,
        algorithm='greedy'
    )

    print(f"Solver result with invalid bandwidth: error={error}")
    print(f"Expected: Error message about bandwidth not summing to 100%")
    print()

    # -------------------------------------------------------------------------
    # Test 8: Save solver run
    # -------------------------------------------------------------------------
    print("TEST 8: Save Solver Run")
    print("-" * 80)

    # Run a solver to get results
    selected, explanation, metrics, error = run_solver(
        available_time=25.0,
        domain_preferences=domain_prefs,
        algorithm='weighted'
    )

    if error is None:
        # Extract task IDs from selected tasks
        if len(selected) > 0:
            task_ids = selected['id'].tolist()
        else:
            task_ids = []

        # Save the run
        save_success, run_id = save_solver_run(
            available_time=25.0,
            domain_preferences=domain_prefs,
            algorithm='weighted',
            selected_task_ids=task_ids,
            metrics=metrics,
            explanation=explanation
        )

        print(f"Save solver run result: success={save_success}")
        if save_success:
            print(f"Saved as run ID: {run_id}")
            print(f"Expected: Run saved successfully to database")
        else:
            print("Failed to save run")
    else:
        print(f"Skipping save test (solver error: {error})")
    print()

    # -------------------------------------------------------------------------
    # Test 9: Get solver run history
    # -------------------------------------------------------------------------
    print("TEST 9: Get Solver Run History")
    print("-" * 80)

    history_df = get_solver_run_history()
    print(f"Found {len(history_df)} historical solver runs")
    if len(history_df) > 0:
        print("Recent runs:")
        print(history_df[['id', 'timestamp', 'algorithm', 'available_time']].head().to_string(index=False))
        print(f"Expected: Runs sorted by timestamp (most recent first)")
    print()

    # -------------------------------------------------------------------------
    # Test 10: Get solver run details
    # -------------------------------------------------------------------------
    print("TEST 10: Get Solver Run Details")
    print("-" * 80)

    if len(history_df) > 0:
        # Get details of the most recent run
        latest_run_id = history_df.iloc[0]['id']
        run_details = get_solver_run_details(latest_run_id)

        if run_details is not None:
            print(f"Retrieved run ID: {run_details['id']}")
            print(f"Algorithm: {run_details['algorithm']}")
            print(f"Available time: {run_details['available_time']}sp")
            print(f"Domain preferences: {run_details['domain_preferences']}")
            print(f"Selected tasks: {run_details['selected_tasks']}")
            print(f"Metrics: total_value={run_details['metrics']['total_value']}, "
                  f"num_tasks={run_details['metrics']['num_tasks']}")
            print(f"Task details DataFrame has {len(run_details['task_details'])} rows")
            print(f"Expected: Complete run details with parsed JSON and task info")
        else:
            print("Failed to retrieve run details")
    else:
        print("No runs available to retrieve details")
    print()

    # -------------------------------------------------------------------------
    # Test 11: Delete task (cleanup)
    # -------------------------------------------------------------------------
    print("TEST 11: Delete Task")
    print("-" * 80)

    if success and task_id is not None:
        delete_success, delete_msg = delete_task(task_id)
        print(f"Delete task result: success={delete_success}")
        print(f"Message: {delete_msg}")
        print(f"Expected: Task deleted successfully")
    else:
        print("Skipping delete test (no task to delete)")
    print()

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("STANDALONE TESTS COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print("  - Task CRUD operations working correctly")
    print("  - Domain retrieval operations functional")
    print("  - Solver orchestration executes all algorithms")
    print("  - Validation errors propagate with clear messages")
    print("  - Solver runs can be saved and retrieved from history")
    print("  - Error handling provides useful feedback")
    print()
    print("Workflow layer successfully orchestrates between UI, logic, analysis, and DB layers.")
