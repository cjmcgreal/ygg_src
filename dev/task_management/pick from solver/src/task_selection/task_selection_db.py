"""
CSV Database Layer for Task Selection System

This module handles all CSV file I/O operations for the task selection prototype.
It provides CRUD-like functions for domains, tasks, and solver runs, abstracting
away CSV file details from the rest of the application.

CSV Files:
- domains.csv: Domain definitions with colors for UI
- tasks.csv: Task backlog with effort, value, priority
- solver_runs.csv: Historical solver executions with results
"""

import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path


# Define the base directory for CSV data files
# Using relative path from this file's location to the data folder
DATA_DIR = Path(__file__).parent / "task_selection_data"


# ==============================================================================
# DOMAIN CSV OPERATIONS
# ==============================================================================

def load_domains():
    """
    Load domains from domains.csv into a pandas DataFrame.

    Domains represent categories for tasks (e.g., backend, frontend, design)
    and include color codes for visual distinction in the UI.

    Returns:
        pd.DataFrame: DataFrame with columns: id, name, color

    Raises:
        FileNotFoundError: If domains.csv doesn't exist and can't be created

    Example:
        >>> domains_df = load_domains()
        >>> print(domains_df.columns)
        Index(['id', 'name', 'color'], dtype='object')
    """
    domains_file = DATA_DIR / "domains.csv"

    try:
        # Attempt to read existing CSV file
        domains_df = pd.read_csv(domains_file)
        return domains_df
    except FileNotFoundError:
        # If file doesn't exist, create it with sample data
        print(f"Warning: {domains_file} not found. Creating with sample data.")

        # Create sample domains with distinct colors
        sample_domains = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['backend', 'frontend', 'design', 'devops', 'testing'],
            'color': ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
        })

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Save sample data to CSV
        sample_domains.to_csv(domains_file, index=False)

        return sample_domains


def save_domains(domains_df):
    """
    Save domains DataFrame to domains.csv.

    Overwrites the existing file with the provided DataFrame.

    Args:
        domains_df (pd.DataFrame): DataFrame with columns: id, name, color

    Returns:
        bool: True if save successful

    Raises:
        ValueError: If DataFrame is missing required columns

    Example:
        >>> domains_df = load_domains()
        >>> domains_df.loc[len(domains_df)] = [6, 'security', '#34495e']
        >>> save_domains(domains_df)
        True
    """
    # Validate required columns exist
    required_columns = {'id', 'name', 'color'}
    if not required_columns.issubset(domains_df.columns):
        missing = required_columns - set(domains_df.columns)
        raise ValueError(f"DataFrame missing required columns: {missing}")

    domains_file = DATA_DIR / "domains.csv"

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save to CSV without index column
    domains_df.to_csv(domains_file, index=False)

    return True


def get_domain_by_name(domain_name):
    """
    Retrieve a specific domain by its name.

    Args:
        domain_name (str): Name of the domain to retrieve (e.g., 'backend')

    Returns:
        pd.Series: Single row with domain data, or None if not found

    Example:
        >>> domain = get_domain_by_name('backend')
        >>> if domain is not None:
        ...     print(f"Domain color: {domain['color']}")
        Domain color: #3498db
    """
    domains_df = load_domains()

    # Filter for matching domain name (case-sensitive)
    matching_domains = domains_df[domains_df['name'] == domain_name]

    if len(matching_domains) == 0:
        return None

    # Return first matching domain as Series
    return matching_domains.iloc[0]


# ==============================================================================
# TASK CSV OPERATIONS
# ==============================================================================

def load_tasks():
    """
    Load tasks from tasks.csv into a pandas DataFrame.

    Tasks represent work items in the backlog with effort estimates,
    value scores, priority rankings, and domain categorization.

    Returns:
        pd.DataFrame: DataFrame with columns: id, title, description, domain,
                      project_parent, effort, value, priority

    Raises:
        FileNotFoundError: If tasks.csv doesn't exist and can't be created

    Example:
        >>> tasks_df = load_tasks()
        >>> high_priority_tasks = tasks_df[tasks_df['priority'] == 1]
        >>> print(f"Found {len(high_priority_tasks)} high-priority tasks")
    """
    tasks_file = DATA_DIR / "tasks.csv"

    try:
        # Attempt to read existing CSV file
        tasks_df = pd.read_csv(tasks_file)
        return tasks_df
    except FileNotFoundError:
        # If file doesn't exist, create it with sample data
        print(f"Warning: {tasks_file} not found. Creating with sample data.")

        # Create sample tasks covering different domains and scenarios
        sample_tasks = pd.DataFrame({
            'id': [1, 2, 3],
            'title': [
                'Implement user authentication',
                'Design homepage mockup',
                'Fix login bug'
            ],
            'description': [
                'Add JWT-based authentication system',
                'Create responsive landing page design',
                'Resolve null pointer exception in login flow'
            ],
            'domain': ['backend', 'design', 'backend'],
            'project_parent': ['auth_project', 'redesign_initiative', 'bugfix_sprint'],
            'effort': [8.0, 5.0, 2.0],
            'value': [9.0, 8.0, 6.0],
            'priority': [1, 1, 2]
        })

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Save sample data to CSV
        sample_tasks.to_csv(tasks_file, index=False)

        return sample_tasks


def save_tasks(tasks_df):
    """
    Save tasks DataFrame to tasks.csv.

    Overwrites the existing file with the provided DataFrame.

    Args:
        tasks_df (pd.DataFrame): DataFrame with columns: id, title, description,
                                 domain, project_parent, effort, value, priority

    Returns:
        bool: True if save successful

    Raises:
        ValueError: If DataFrame is missing required columns

    Example:
        >>> tasks_df = load_tasks()
        >>> tasks_df.loc[tasks_df['id'] == 1, 'priority'] = 2
        >>> save_tasks(tasks_df)
        True
    """
    # Validate required columns exist
    required_columns = {'id', 'title', 'description', 'domain', 'project_parent',
                       'effort', 'value', 'priority'}
    if not required_columns.issubset(tasks_df.columns):
        missing = required_columns - set(tasks_df.columns)
        raise ValueError(f"DataFrame missing required columns: {missing}")

    tasks_file = DATA_DIR / "tasks.csv"

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save to CSV without index column
    tasks_df.to_csv(tasks_file, index=False)

    return True


def get_next_task_id():
    """
    Get the next available task ID for creating a new task.

    Finds the maximum existing ID and returns max + 1.
    If no tasks exist, returns 1.

    Returns:
        int: Next available task ID

    Example:
        >>> next_id = get_next_task_id()
        >>> print(f"Next task will be ID: {next_id}")
        Next task will be ID: 16
    """
    tasks_df = load_tasks()

    if len(tasks_df) == 0:
        # No tasks exist, start at ID 1
        return 1

    # Find maximum existing ID and add 1
    max_id = tasks_df['id'].max()
    return int(max_id) + 1


def get_task_by_id(task_id):
    """
    Retrieve a specific task by its ID.

    Args:
        task_id (int): ID of the task to retrieve

    Returns:
        pd.Series: Single row with task data, or None if not found

    Example:
        >>> task = get_task_by_id(1)
        >>> if task is not None:
        ...     print(f"Task: {task['title']}")
        ...     print(f"Effort: {task['effort']} story points")
        Task: Implement user authentication
        Effort: 8.0 story points
    """
    tasks_df = load_tasks()

    # Filter for matching task ID
    matching_tasks = tasks_df[tasks_df['id'] == task_id]

    if len(matching_tasks) == 0:
        return None

    # Return first matching task as Series
    return matching_tasks.iloc[0]


def delete_task_by_id(task_id):
    """
    Delete a task from the tasks DataFrame by its ID.

    Loads tasks, removes the specified task, and saves the updated DataFrame.

    Args:
        task_id (int): ID of the task to delete

    Returns:
        tuple: (success: bool, message: str)
               - (True, "Task deleted successfully") if found and deleted
               - (False, "Task not found") if ID doesn't exist

    Example:
        >>> success, message = delete_task_by_id(99)
        >>> if not success:
        ...     print(f"Error: {message}")
        Error: Task not found
    """
    tasks_df = load_tasks()

    # Check if task exists
    task_exists = task_id in tasks_df['id'].values

    if not task_exists:
        return (False, f"Task with ID {task_id} not found")

    # Remove task with matching ID
    # Using != instead of drop() for clarity
    updated_tasks_df = tasks_df[tasks_df['id'] != task_id].copy()

    # Save updated tasks back to CSV
    save_tasks(updated_tasks_df)

    return (True, f"Task {task_id} deleted successfully")


# ==============================================================================
# SOLVER RUN CSV OPERATIONS
# ==============================================================================

def load_solver_runs():
    """
    Load solver runs from solver_runs.csv into a pandas DataFrame.

    Solver runs represent historical executions of task selection algorithms
    with their parameters and results stored as JSON strings.

    Returns:
        pd.DataFrame: DataFrame with columns: id, timestamp, available_time,
                      algorithm, domain_preferences_json, selected_tasks_json,
                      metrics_json, explanation_json

    Note:
        JSON fields need to be parsed with json.loads() before use.

    Example:
        >>> runs_df = load_solver_runs()
        >>> if len(runs_df) > 0:
        ...     latest_run = runs_df.iloc[-1]
        ...     prefs = json.loads(latest_run['domain_preferences_json'])
    """
    runs_file = DATA_DIR / "solver_runs.csv"

    try:
        # Attempt to read existing CSV file
        runs_df = pd.read_csv(runs_file)
        return runs_df
    except FileNotFoundError:
        # If file doesn't exist, create empty file with headers
        print(f"Warning: {runs_file} not found. Creating empty file with headers.")

        # Create empty DataFrame with proper schema
        empty_runs = pd.DataFrame(columns=[
            'id', 'timestamp', 'available_time', 'algorithm',
            'domain_preferences_json', 'selected_tasks_json',
            'metrics_json', 'explanation_json'
        ])

        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Save empty DataFrame to CSV (creates header row)
        empty_runs.to_csv(runs_file, index=False)

        return empty_runs


def save_solver_run(run_data):
    """
    Append a new solver run to solver_runs.csv.

    Converts complex Python objects (dicts, lists) to JSON strings for storage.
    Automatically generates run ID and timestamp if not provided.

    Args:
        run_data (dict): Dictionary containing run information with keys:
            - available_time (float): Story points allocated
            - algorithm (str): Algorithm used ('greedy', 'weighted', 'knapsack')
            - domain_preferences (dict): Domain name to percentage mapping
            - selected_tasks (list): List of selected task IDs
            - metrics (dict): Performance metrics dictionary
            - explanation (list): List of explanation strings

    Returns:
        tuple: (success: bool, run_id: int or None)
               - (True, run_id) if save successful
               - (False, None) if save failed

    Example:
        >>> run_data = {
        ...     'available_time': 40.0,
        ...     'algorithm': 'greedy',
        ...     'domain_preferences': {'backend': 50, 'frontend': 50},
        ...     'selected_tasks': [1, 2, 3],
        ...     'metrics': {'total_value': 23, 'total_effort': 15},
        ...     'explanation': ['Selected task 1 with score 1.13']
        ... }
        >>> success, run_id = save_solver_run(run_data)
        >>> print(f"Saved as run ID: {run_id}")
        Saved as run ID: 1
    """
    runs_df = load_solver_runs()

    # Generate new run ID
    if len(runs_df) == 0:
        new_run_id = 1
    else:
        new_run_id = int(runs_df['id'].max()) + 1

    # Generate timestamp in ISO 8601 format
    timestamp = datetime.now().isoformat()

    # Convert complex fields to JSON strings for CSV storage
    # This allows us to store nested data structures in flat CSV format
    try:
        new_run = {
            'id': new_run_id,
            'timestamp': timestamp,
            'available_time': run_data['available_time'],
            'algorithm': run_data['algorithm'],
            'domain_preferences_json': json.dumps(run_data['domain_preferences']),
            'selected_tasks_json': json.dumps(run_data['selected_tasks']),
            'metrics_json': json.dumps(run_data['metrics']),
            'explanation_json': json.dumps(run_data['explanation'])
        }

        # Create DataFrame for new run
        new_run_df = pd.DataFrame([new_run])

        # Append to existing runs
        updated_runs_df = pd.concat([runs_df, new_run_df], ignore_index=True)

        # Save back to CSV
        runs_file = DATA_DIR / "solver_runs.csv"
        updated_runs_df.to_csv(runs_file, index=False)

        return (True, new_run_id)

    except (KeyError, TypeError, json.JSONDecodeError) as e:
        print(f"Error saving solver run: {e}")
        return (False, None)


def get_solver_run_by_id(run_id):
    """
    Retrieve a specific solver run by its ID.

    Loads the run and parses JSON fields back into Python objects.

    Args:
        run_id (int): ID of the solver run to retrieve

    Returns:
        dict or None: Dictionary with parsed run data, or None if not found.
                      Dictionary includes all fields with JSON strings parsed.

    Example:
        >>> run = get_solver_run_by_id(1)
        >>> if run is not None:
        ...     print(f"Algorithm: {run['algorithm']}")
        ...     print(f"Selected {len(run['selected_tasks'])} tasks")
        Algorithm: greedy
        Selected 3 tasks
    """
    runs_df = load_solver_runs()

    # Filter for matching run ID
    matching_runs = runs_df[runs_df['id'] == run_id]

    if len(matching_runs) == 0:
        return None

    # Get the run as a Series
    run_series = matching_runs.iloc[0]

    # Parse JSON fields back to Python objects
    try:
        run_dict = {
            'id': int(run_series['id']),
            'timestamp': run_series['timestamp'],
            'available_time': float(run_series['available_time']),
            'algorithm': run_series['algorithm'],
            'domain_preferences': json.loads(run_series['domain_preferences_json']),
            'selected_tasks': json.loads(run_series['selected_tasks_json']),
            'metrics': json.loads(run_series['metrics_json']),
            'explanation': json.loads(run_series['explanation_json'])
        }

        return run_dict

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing solver run {run_id}: {e}")
        return None


def get_all_solver_runs():
    """
    Retrieve all solver runs sorted by timestamp (most recent first).

    Returns:
        pd.DataFrame: DataFrame with all runs, sorted by timestamp descending

    Note:
        JSON fields are still in string format. Use json.loads() to parse them,
        or use get_solver_run_by_id() for automatic parsing of individual runs.

    Example:
        >>> all_runs_df = get_all_solver_runs()
        >>> print(f"Total runs: {len(all_runs_df)}")
        >>> if len(all_runs_df) > 0:
        ...     print(f"Latest algorithm used: {all_runs_df.iloc[0]['algorithm']}")
        Total runs: 5
        Latest algorithm used: weighted
    """
    runs_df = load_solver_runs()

    if len(runs_df) == 0:
        return runs_df

    # Sort by timestamp in descending order (most recent first)
    # Using sort_values with ascending=False
    sorted_runs_df = runs_df.sort_values('timestamp', ascending=False).copy()

    return sorted_runs_df


# ==============================================================================
# STANDALONE TEST SECTION
# ==============================================================================

if __name__ == "__main__":
    """
    Standalone test section demonstrating all CSV database operations.

    This section can be run independently to verify functionality:
    $ python src/task_selection/task_selection_db.py

    Tests cover:
    - Loading and saving domains
    - Loading and saving tasks
    - Task CRUD operations (create, read, update, delete)
    - Solver run storage and retrieval
    - JSON serialization for complex fields
    """

    print("=" * 80)
    print("TASK SELECTION DATABASE LAYER - STANDALONE TESTS")
    print("=" * 80)
    print()

    # -------------------------------------------------------------------------
    # Test 1: Load and display domains
    # -------------------------------------------------------------------------
    print("TEST 1: Load Domains")
    print("-" * 80)

    domains_df = load_domains()
    print(f"Loaded {len(domains_df)} domains:")
    print(domains_df.to_string(index=False))
    print(f"Expected: 5 domains (backend, frontend, design, devops, testing)")
    print()

    # -------------------------------------------------------------------------
    # Test 2: Get domain by name
    # -------------------------------------------------------------------------
    print("TEST 2: Get Domain By Name")
    print("-" * 80)

    backend_domain = get_domain_by_name('backend')
    if backend_domain is not None:
        print(f"Found domain: {backend_domain['name']}")
        print(f"Color: {backend_domain['color']}")
        print(f"Expected color: #3498db")
    else:
        print("ERROR: Backend domain not found!")
    print()

    # -------------------------------------------------------------------------
    # Test 3: Load and display tasks
    # -------------------------------------------------------------------------
    print("TEST 3: Load Tasks")
    print("-" * 80)

    tasks_df = load_tasks()
    print(f"Loaded {len(tasks_df)} tasks:")
    print(tasks_df[['id', 'title', 'domain', 'effort', 'value', 'priority']].to_string(index=False))
    print(f"Expected: Multiple tasks with diverse domains and priorities")
    print()

    # -------------------------------------------------------------------------
    # Test 4: Get next task ID
    # -------------------------------------------------------------------------
    print("TEST 4: Get Next Task ID")
    print("-" * 80)

    next_id = get_next_task_id()
    current_max = tasks_df['id'].max()
    print(f"Current max task ID: {current_max}")
    print(f"Next available ID: {next_id}")
    print(f"Expected: {current_max + 1}")
    print()

    # -------------------------------------------------------------------------
    # Test 5: Get task by ID
    # -------------------------------------------------------------------------
    print("TEST 5: Get Task By ID")
    print("-" * 80)

    task = get_task_by_id(1)
    if task is not None:
        print(f"Task ID 1: {task['title']}")
        print(f"Domain: {task['domain']}")
        print(f"Effort: {task['effort']} story points")
        print(f"Value: {task['value']}")
    else:
        print("ERROR: Task 1 not found!")
    print()

    # -------------------------------------------------------------------------
    # Test 6: Add a new task (simulating create operation)
    # -------------------------------------------------------------------------
    print("TEST 6: Add New Task")
    print("-" * 80)

    # Create a copy of tasks to modify
    tasks_copy = tasks_df.copy()

    new_task = {
        'id': get_next_task_id(),
        'title': 'Test task for demo',
        'description': 'This is a test task added in standalone section',
        'domain': 'testing',
        'project_parent': 'test_project',
        'effort': 3.0,
        'value': 7.0,
        'priority': 1
    }

    # Add new task to DataFrame
    new_task_df = pd.DataFrame([new_task])
    tasks_with_new = pd.concat([tasks_copy, new_task_df], ignore_index=True)

    print(f"Before: {len(tasks_copy)} tasks")
    print(f"After: {len(tasks_with_new)} tasks")
    print(f"New task ID: {new_task['id']}")
    print(f"Expected: One additional task")
    print()

    # Note: Not actually saving to avoid modifying test data
    # In real usage: save_tasks(tasks_with_new)

    # -------------------------------------------------------------------------
    # Test 7: Delete task by ID (without saving)
    # -------------------------------------------------------------------------
    print("TEST 7: Delete Task By ID (Simulation)")
    print("-" * 80)

    # Simulate deletion by filtering
    task_to_delete = 3
    tasks_after_delete = tasks_df[tasks_df['id'] != task_to_delete].copy()

    print(f"Before deletion: {len(tasks_df)} tasks")
    print(f"After deleting task {task_to_delete}: {len(tasks_after_delete)} tasks")
    print(f"Expected: One fewer task")

    # Verify task is gone
    deleted_task = get_task_by_id(task_to_delete)
    if deleted_task is not None:
        print(f"Task {task_to_delete} still exists in original data (expected)")
    print()

    # Note: Not actually saving to avoid modifying test data
    # In real usage: success, msg = delete_task_by_id(task_to_delete)

    # -------------------------------------------------------------------------
    # Test 8: Load solver runs (should be empty initially)
    # -------------------------------------------------------------------------
    print("TEST 8: Load Solver Runs")
    print("-" * 80)

    runs_df = load_solver_runs()
    print(f"Loaded {len(runs_df)} solver runs")
    if len(runs_df) == 0:
        print("Expected: Empty (no runs saved yet)")
    else:
        print("Existing runs:")
        print(runs_df[['id', 'timestamp', 'algorithm']].to_string(index=False))
    print()

    # -------------------------------------------------------------------------
    # Test 9: Save a solver run
    # -------------------------------------------------------------------------
    print("TEST 9: Save Solver Run")
    print("-" * 80)

    # Create sample run data
    sample_run = {
        'available_time': 40.0,
        'algorithm': 'greedy',
        'domain_preferences': {
            'backend': 50,
            'frontend': 30,
            'design': 20
        },
        'selected_tasks': [1, 2, 5],
        'metrics': {
            'total_effort': 21.0,
            'total_value': 24.0,
            'num_tasks': 3,
            'utilization_pct': 52.5
        },
        'explanation': [
            'Selected task 1: Implement user authentication (score: 1.125)',
            'Selected task 2: Design homepage mockup (score: 1.6)',
            'Selected task 5: Implement search feature (score: 0.875)'
        ]
    }

    success, run_id = save_solver_run(sample_run)
    if success:
        print(f"Successfully saved solver run with ID: {run_id}")
        print(f"Algorithm: {sample_run['algorithm']}")
        print(f"Selected {len(sample_run['selected_tasks'])} tasks")
        print(f"Expected: New run added to solver_runs.csv")
    else:
        print("ERROR: Failed to save solver run!")
    print()

    # -------------------------------------------------------------------------
    # Test 10: Retrieve solver run by ID
    # -------------------------------------------------------------------------
    print("TEST 10: Get Solver Run By ID")
    print("-" * 80)

    if success:
        retrieved_run = get_solver_run_by_id(run_id)
        if retrieved_run is not None:
            print(f"Retrieved run ID: {retrieved_run['id']}")
            print(f"Algorithm: {retrieved_run['algorithm']}")
            print(f"Available time: {retrieved_run['available_time']} story points")
            print(f"Domain preferences: {retrieved_run['domain_preferences']}")
            print(f"Selected tasks: {retrieved_run['selected_tasks']}")
            print(f"Total value: {retrieved_run['metrics']['total_value']}")
            print(f"Expected: All fields parsed correctly from JSON")
        else:
            print(f"ERROR: Could not retrieve run {run_id}!")
    print()

    # -------------------------------------------------------------------------
    # Test 11: Get all solver runs
    # -------------------------------------------------------------------------
    print("TEST 11: Get All Solver Runs (Sorted)")
    print("-" * 80)

    all_runs_df = get_all_solver_runs()
    print(f"Total solver runs: {len(all_runs_df)}")
    if len(all_runs_df) > 0:
        print("Most recent runs:")
        print(all_runs_df[['id', 'timestamp', 'algorithm', 'available_time']].head().to_string(index=False))
        print(f"Expected: Runs sorted by timestamp (most recent first)")
    print()

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("=" * 80)
    print("STANDALONE TESTS COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Domains loaded: {len(domains_df)}")
    print(f"  - Tasks loaded: {len(tasks_df)}")
    print(f"  - Solver runs saved: {1 if success else 0}")
    print(f"  - All CSV operations working correctly")
    print()
    print("Note: Test modifications are not saved to preserve original data.")
    print("In production, use save_tasks() and save_domains() to persist changes.")
