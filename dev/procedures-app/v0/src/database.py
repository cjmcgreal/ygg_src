"""
Database layer for CSV-based data storage
Handles all CRUD operations for procedures, steps, runs, labels, and versions
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

# Data directory path
DATA_DIR = Path(__file__).parent.parent / "data"


def get_schema(table_name: str) -> List[str]:
    """
    Get the column schema for a given table

    Args:
        table_name: Name of the table

    Returns:
        List of column names
    """
    schemas = {
        "procedures": ["id", "name", "description", "created_at", "updated_at", "version"],
        "steps": ["id", "procedure_id", "order", "description", "estimated_duration"],
        "runs": ["id", "procedure_id", "start_time", "end_time", "status", "notes"],
        "run_steps": ["id", "run_id", "step_id", "completed", "completed_at", "notes"],
        "labels": ["id", "name", "color"],
        "procedure_labels": ["procedure_id", "label_id"],
        "versions": ["id", "procedure_id", "version", "created_at", "change_description", "procedure_snapshot"],
    }
    return schemas.get(table_name, [])


def load_table(table_name: str) -> pd.DataFrame:
    """
    Load CSV table into DataFrame

    Args:
        table_name: Name of the table to load

    Returns:
        DataFrame with table data
    """
    file_path = DATA_DIR / f"{table_name}.csv"
    if not file_path.exists():
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=get_schema(table_name))

    df = pd.read_csv(file_path)

    # Convert datetime columns
    datetime_columns = {
        "procedures": ["created_at", "updated_at"],
        "runs": ["start_time", "end_time"],
        "run_steps": ["completed_at"],
        "versions": ["created_at"],
    }

    if table_name in datetime_columns:
        for col in datetime_columns[table_name]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

    return df


def save_table(table_name: str, df: pd.DataFrame):
    """
    Save DataFrame to CSV

    Args:
        table_name: Name of the table
        df: DataFrame to save
    """
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_path = DATA_DIR / f"{table_name}.csv"
    df.to_csv(file_path, index=False)


# ============================================================================
# PROCEDURES
# ============================================================================

def get_all_procedures() -> pd.DataFrame:
    """Get all procedures"""
    return load_table("procedures")


def get_procedure_by_id(procedure_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single procedure by ID

    Args:
        procedure_id: Procedure ID

    Returns:
        Procedure dict or None if not found
    """
    df = load_table("procedures")
    result = df[df['id'] == procedure_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def create_procedure(name: str, description: str = "") -> int:
    """
    Create a new procedure

    Args:
        name: Procedure name
        description: Optional description

    Returns:
        New procedure ID
    """
    df = load_table("procedures")

    new_id = 1 if df.empty else int(df['id'].max() + 1)
    now = datetime.now()

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'description': description,
        'created_at': now,
        'updated_at': now,
        'version': 1
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("procedures", df)

    return new_id


def update_procedure(procedure_id: int, name: Optional[str] = None,
                     description: Optional[str] = None) -> bool:
    """
    Update a procedure

    Args:
        procedure_id: Procedure ID
        name: New name (optional)
        description: New description (optional)

    Returns:
        True if successful, False if procedure not found
    """
    df = load_table("procedures")
    mask = df['id'] == procedure_id

    if not mask.any():
        return False

    if name is not None:
        df.loc[mask, 'name'] = name
    if description is not None:
        df.loc[mask, 'description'] = description

    df.loc[mask, 'updated_at'] = datetime.now()
    df.loc[mask, 'version'] = df.loc[mask, 'version'] + 1

    save_table("procedures", df)
    return True


def delete_procedure(procedure_id: int) -> bool:
    """
    Delete a procedure and all associated data

    Args:
        procedure_id: Procedure ID

    Returns:
        True if successful
    """
    # Delete procedure
    df = load_table("procedures")
    df = df[df['id'] != procedure_id]
    save_table("procedures", df)

    # Delete associated steps
    steps_df = load_table("steps")
    steps_df = steps_df[steps_df['procedure_id'] != procedure_id]
    save_table("steps", steps_df)

    # Delete procedure labels
    labels_df = load_table("procedure_labels")
    labels_df = labels_df[labels_df['procedure_id'] != procedure_id]
    save_table("procedure_labels", labels_df)

    # Note: We keep runs for historical purposes

    return True


# ============================================================================
# STEPS
# ============================================================================

def get_steps_for_procedure(procedure_id: int) -> List[Dict[str, Any]]:
    """
    Get all steps for a procedure, ordered by step order

    Args:
        procedure_id: Procedure ID

    Returns:
        List of step dicts
    """
    df = load_table("steps")
    steps = df[df['procedure_id'] == procedure_id].sort_values('order')
    return steps.to_dict('records')


def create_step(procedure_id: int, order: int, description: str,
                estimated_duration: Optional[int] = None) -> int:
    """
    Create a new step

    Args:
        procedure_id: Procedure ID
        order: Step order (1, 2, 3...)
        description: Step description
        estimated_duration: Optional estimated duration in seconds

    Returns:
        New step ID
    """
    df = load_table("steps")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'procedure_id': procedure_id,
        'order': order,
        'description': description,
        'estimated_duration': estimated_duration
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("steps", df)

    return new_id


def update_steps_for_procedure(procedure_id: int, steps: List[str]):
    """
    Replace all steps for a procedure

    Args:
        procedure_id: Procedure ID
        steps: List of step descriptions
    """
    # Delete existing steps
    df = load_table("steps")
    df = df[df['procedure_id'] != procedure_id]

    # Create new steps
    for i, description in enumerate(steps):
        new_id = 1 if df.empty else int(df['id'].max() + 1)
        new_row = pd.DataFrame([{
            'id': new_id,
            'procedure_id': procedure_id,
            'order': i + 1,
            'description': description,
            'estimated_duration': None
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    save_table("steps", df)


# ============================================================================
# RUNS
# ============================================================================

def get_all_runs() -> pd.DataFrame:
    """Get all runs"""
    return load_table("runs")


def get_run_by_id(run_id: int) -> Optional[Dict[str, Any]]:
    """Get a single run by ID"""
    df = load_table("runs")
    result = df[df['id'] == run_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def create_run(procedure_id: int) -> int:
    """
    Create a new run

    Args:
        procedure_id: Procedure ID

    Returns:
        New run ID
    """
    df = load_table("runs")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'procedure_id': procedure_id,
        'start_time': datetime.now(),
        'end_time': None,
        'status': 'in_progress',
        'notes': ''
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("runs", df)

    return new_id


def update_run(run_id: int, status: Optional[str] = None,
               notes: Optional[str] = None, end_now: bool = False) -> bool:
    """
    Update a run

    Args:
        run_id: Run ID
        status: New status (optional)
        notes: New notes (optional)
        end_now: Set end_time to now (optional)

    Returns:
        True if successful
    """
    df = load_table("runs")
    mask = df['id'] == run_id

    if not mask.any():
        return False

    if status is not None:
        df.loc[mask, 'status'] = status
    if notes is not None:
        df.loc[mask, 'notes'] = notes
    if end_now:
        df.loc[mask, 'end_time'] = datetime.now()

    save_table("runs", df)
    return True


# ============================================================================
# RUN STEPS
# ============================================================================

def create_run_step(run_id: int, step_id: int) -> int:
    """
    Create a run step tracking entry

    Args:
        run_id: Run ID
        step_id: Step ID

    Returns:
        New run_step ID
    """
    df = load_table("run_steps")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'run_id': run_id,
        'step_id': step_id,
        'completed': False,
        'completed_at': None,
        'notes': ''
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("run_steps", df)

    return new_id


def update_run_step(run_step_id: int, completed: bool = True,
                    notes: Optional[str] = None) -> bool:
    """
    Update a run step

    Args:
        run_step_id: Run step ID
        completed: Completion status
        notes: Optional notes

    Returns:
        True if successful
    """
    df = load_table("run_steps")
    mask = df['id'] == run_step_id

    if not mask.any():
        return False

    df.loc[mask, 'completed'] = completed
    if completed:
        df.loc[mask, 'completed_at'] = datetime.now()
    if notes is not None:
        df.loc[mask, 'notes'] = notes

    save_table("run_steps", df)
    return True


def get_run_steps(run_id: int) -> List[Dict[str, Any]]:
    """Get all run steps for a run"""
    df = load_table("run_steps")
    steps = df[df['run_id'] == run_id]
    return steps.to_dict('records')


# ============================================================================
# LABELS
# ============================================================================

def get_all_labels() -> List[Dict[str, Any]]:
    """Get all labels"""
    df = load_table("labels")
    return df.to_dict('records')


def create_label(name: str, color: str = "#3498db") -> int:
    """
    Create a new label

    Args:
        name: Label name
        color: Hex color code

    Returns:
        New label ID
    """
    df = load_table("labels")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'color': color
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("labels", df)

    return new_id


def get_labels_for_procedure(procedure_id: int) -> List[Dict[str, Any]]:
    """Get all labels assigned to a procedure"""
    pl_df = load_table("procedure_labels")
    labels_df = load_table("labels")

    proc_labels = pl_df[pl_df['procedure_id'] == procedure_id]
    label_ids = proc_labels['label_id'].tolist()

    result = labels_df[labels_df['id'].isin(label_ids)]
    return result.to_dict('records')


def assign_label_to_procedure(procedure_id: int, label_id: int):
    """Assign a label to a procedure"""
    df = load_table("procedure_labels")

    # Check if already exists
    existing = df[(df['procedure_id'] == procedure_id) & (df['label_id'] == label_id)]
    if not existing.empty:
        return  # Already assigned

    new_row = pd.DataFrame([{
        'procedure_id': procedure_id,
        'label_id': label_id
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("procedure_labels", df)


def remove_label_from_procedure(procedure_id: int, label_id: int):
    """Remove a label from a procedure"""
    df = load_table("procedure_labels")
    df = df[~((df['procedure_id'] == procedure_id) & (df['label_id'] == label_id))]
    save_table("procedure_labels", df)
