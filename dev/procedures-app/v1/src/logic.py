"""
Business logic for the Procedures Management App
Orchestrates database operations and implements core business rules
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import json

from . import database
from . import utils


def create_procedure_with_steps(name: str, description: str, steps: List[str]) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Create a complete procedure with steps

    Args:
        name: Procedure name
        description: Procedure description
        steps: List of step descriptions

    Returns:
        Tuple of (success, procedure_id, error_message)
    """
    # Validate input
    is_valid, error = utils.validate_procedure_data(name, steps)
    if not is_valid:
        return False, None, error

    # Create procedure
    procedure_id = database.create_procedure(name, description)

    # Create steps
    database.update_steps_for_procedure(procedure_id, steps)

    # Create initial version
    create_version_snapshot(procedure_id, "Initial creation")

    return True, procedure_id, None


def update_procedure_with_steps(procedure_id: int, name: Optional[str] = None,
                                 description: Optional[str] = None,
                                 steps: Optional[List[str]] = None,
                                 change_description: str = "Updated procedure") -> Tuple[bool, Optional[str]]:
    """
    Update a procedure and optionally its steps

    Args:
        procedure_id: Procedure ID
        name: New name (optional)
        description: New description (optional)
        steps: New steps list (optional)
        change_description: Description of changes for version history

    Returns:
        Tuple of (success, error_message)
    """
    # Validate procedure exists
    procedure = database.get_procedure_by_id(procedure_id)
    if not procedure:
        return False, "Procedure not found"

    # Validate steps if provided
    if steps is not None:
        is_valid, error = utils.validate_procedure_data(
            name or procedure['name'],
            steps
        )
        if not is_valid:
            return False, error

    # Update procedure
    if name or description:
        database.update_procedure(procedure_id, name, description)

    # Update steps
    if steps is not None:
        database.update_steps_for_procedure(procedure_id, steps)

    # Create version snapshot
    create_version_snapshot(procedure_id, change_description)

    return True, None


def start_procedure_run(procedure_id: int) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Start executing a procedure

    Args:
        procedure_id: Procedure ID

    Returns:
        Tuple of (success, run_id, error_message)
    """
    # Validate procedure exists
    procedure = database.get_procedure_by_id(procedure_id)
    if not procedure:
        return False, None, "Procedure not found"

    # Get steps
    steps = database.get_steps_for_procedure(procedure_id)
    if not steps:
        return False, None, "Procedure has no steps"

    # Create run
    run_id = database.create_run(procedure_id)

    # Initialize run steps
    for step in steps:
        database.create_run_step(run_id, step['id'])

    return True, run_id, None


def complete_step_in_run(run_id: int, step_id: int, notes: str = "") -> Tuple[bool, Optional[str]]:
    """
    Mark a step as completed in a run

    Args:
        run_id: Run ID
        step_id: Step ID
        notes: Optional notes

    Returns:
        Tuple of (success, error_message)
    """
    # Get run steps
    run_steps = database.get_run_steps(run_id)

    # Find the specific run_step
    run_step = next((rs for rs in run_steps if rs['step_id'] == step_id), None)
    if not run_step:
        return False, "Step not found in this run"

    # Update run step
    database.update_run_step(run_step['id'], completed=True, notes=notes)

    return True, None


def finish_run(run_id: int, status: str = "completed", notes: str = "") -> Tuple[bool, Optional[str]]:
    """
    Complete or cancel a run

    Args:
        run_id: Run ID
        status: 'completed' or 'cancelled'
        notes: Optional notes

    Returns:
        Tuple of (success, error_message)
    """
    if status not in ['completed', 'cancelled']:
        return False, "Status must be 'completed' or 'cancelled'"

    # Validate run exists
    run = database.get_run_by_id(run_id)
    if not run:
        return False, "Run not found"

    # Update run
    database.update_run(run_id, status=status, notes=notes, end_now=True)

    return True, None


def get_procedure_with_metadata(procedure_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a procedure with additional computed metadata

    Args:
        procedure_id: Procedure ID

    Returns:
        Procedure dict with metadata
    """
    procedure = database.get_procedure_by_id(procedure_id)
    if not procedure:
        return None

    # Get steps
    steps = database.get_steps_for_procedure(procedure_id)

    # Get labels
    labels = database.get_labels_for_procedure(procedure_id)

    # Get run statistics
    runs_df = database.get_all_runs()
    proc_runs = runs_df[runs_df['procedure_id'] == procedure_id]

    total_runs = len(proc_runs)
    completed_runs = len(proc_runs[proc_runs['status'] == 'completed'])

    # Calculate average duration
    completed_with_times = proc_runs[
        (proc_runs['status'] == 'completed') &
        (proc_runs['end_time'].notna())
    ]

    avg_duration = None
    if not completed_with_times.empty:
        durations = (completed_with_times['end_time'] - completed_with_times['start_time']).dt.total_seconds()
        avg_duration = durations.mean()

    # Get last run date
    last_run = None
    if not proc_runs.empty:
        last_run = proc_runs['start_time'].max()

    return {
        **procedure,
        'step_count': len(steps),
        'steps': steps,
        'labels': labels,
        'total_runs': total_runs,
        'completed_runs': completed_runs,
        'avg_duration_seconds': avg_duration,
        'avg_duration_formatted': utils.format_duration(avg_duration) if avg_duration else "N/A",
        'last_run': last_run,
        'completion_rate': utils.safe_divide(completed_runs, total_runs, 0) * 100
    }


def get_all_procedures_with_metadata() -> List[Dict[str, Any]]:
    """
    Get all procedures with metadata

    Returns:
        List of procedure dicts with metadata
    """
    procedures_df = database.get_all_procedures()
    result = []

    for _, proc in procedures_df.iterrows():
        proc_with_meta = get_procedure_with_metadata(proc['id'])
        if proc_with_meta:
            result.append(proc_with_meta)

    return result


def filter_procedures(procedures: List[Dict[str, Any]],
                      search: str = "",
                      label_ids: List[int] = None) -> List[Dict[str, Any]]:
    """
    Filter procedures by search term and labels

    Args:
        procedures: List of procedures
        search: Search term
        label_ids: List of label IDs to filter by

    Returns:
        Filtered list of procedures
    """
    result = procedures

    # Filter by search
    if search:
        search_lower = search.lower()
        result = [
            p for p in result
            if search_lower in p['name'].lower() or
               search_lower in p.get('description', '').lower()
        ]

    # Filter by labels
    if label_ids:
        result = [
            p for p in result
            if any(label['id'] in label_ids for label in p.get('labels', []))
        ]

    return result


def get_run_with_details(run_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a run with full details including steps

    Args:
        run_id: Run ID

    Returns:
        Run dict with details
    """
    run = database.get_run_by_id(run_id)
    if not run:
        return None

    # Get procedure
    procedure = database.get_procedure_by_id(run['procedure_id'])

    # Get run steps with step details
    run_steps = database.get_run_steps(run_id)
    all_steps = database.get_steps_for_procedure(run['procedure_id'])

    # Merge run step status with step details
    steps_with_status = []
    for step in all_steps:
        run_step = next((rs for rs in run_steps if rs['step_id'] == step['id']), None)
        steps_with_status.append({
            **step,
            'completed': run_step['completed'] if run_step else False,
            'completed_at': run_step.get('completed_at') if run_step else None,
            'run_step_notes': run_step.get('notes', '') if run_step else ''
        })

    # Calculate duration
    duration = None
    if run['end_time']:
        duration = utils.calculate_duration_seconds(run['start_time'], run['end_time'])

    return {
        **run,
        'procedure': procedure,
        'steps': steps_with_status,
        'duration_seconds': duration,
        'duration_formatted': utils.format_duration(duration) if duration else "In progress"
    }


def get_all_runs_with_details() -> List[Dict[str, Any]]:
    """
    Get all runs with details

    Returns:
        List of run dicts with details
    """
    runs_df = database.get_all_runs()
    result = []

    for _, run_row in runs_df.iterrows():
        run_details = get_run_with_details(run_row['id'])
        if run_details:
            result.append(run_details)

    # Sort by start time descending (most recent first)
    result.sort(key=lambda x: x['start_time'], reverse=True)

    return result


def create_version_snapshot(procedure_id: int, change_description: str = ""):
    """
    Create a version snapshot of a procedure

    Args:
        procedure_id: Procedure ID
        change_description: Description of what changed
    """
    procedure = database.get_procedure_by_id(procedure_id)
    if not procedure:
        return

    steps = database.get_steps_for_procedure(procedure_id)

    # Create snapshot
    snapshot = {
        'procedure': procedure,
        'steps': steps
    }

    # Save version (note: we would need to add a versions table function)
    # For now, this is a placeholder for future version control feature
    pass


def get_active_run() -> Optional[Dict[str, Any]]:
    """
    Get the currently active (in_progress) run if any

    Returns:
        Run dict or None
    """
    runs_df = database.get_all_runs()
    active = runs_df[runs_df['status'] == 'in_progress']

    if active.empty:
        return None

    # Get the most recent active run
    latest = active.sort_values('start_time', ascending=False).iloc[0]
    return get_run_with_details(latest['id'])


def get_run_progress(run_id: int) -> Dict[str, Any]:
    """
    Calculate progress metrics for a run

    Args:
        run_id: Run ID

    Returns:
        Progress dict with metrics
    """
    run_steps = database.get_run_steps(run_id)

    total_steps = len(run_steps)
    completed_steps = sum(1 for rs in run_steps if rs['completed'])

    progress_percent = utils.safe_divide(completed_steps, total_steps, 0) * 100

    return {
        'total_steps': total_steps,
        'completed_steps': completed_steps,
        'remaining_steps': total_steps - completed_steps,
        'progress_percent': progress_percent
    }
