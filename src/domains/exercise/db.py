"""
Database layer for CSV-based data storage
Handles all CRUD operations for exercises, workouts, workout_logs, and set_logs
Framework-independent - no Streamlit dependencies
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Data directory path
DATA_DIR = Path(__file__).parent / "data"


def get_schema(table_name: str) -> List[str]:
    """
    Get the column schema for a given table

    Args:
        table_name: Name of the table

    Returns:
        List of column names
    """
    schemas = {
        "exercises": [
            "id", "name", "description", "primary_muscle_groups",
            "secondary_muscle_groups", "progression_scheme",
            "rep_range_min", "rep_range_max", "target_reps",
            "rep_increment", "weight_increment", "created_at", "warmup_config"
        ],
        "workouts": [
            "id", "name", "exercise_ids", "created_at", "notes"
        ],
        "workout_logs": [
            "id", "workout_id", "start_time", "end_time",
            "duration_seconds", "total_volume", "total_calories",
            "total_sets", "muscle_groups_trained", "status", "notes"
        ],
        "set_logs": [
            "id", "workout_log_id", "exercise_id", "set_type",
            "set_number", "target_weight", "actual_weight",
            "target_reps", "actual_reps", "rest_seconds",
            "completed", "completed_at", "one_rep_max_estimate",
            "volume", "duration_seconds", "calories", "notes"
        ]
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
        "exercises": ["created_at"],
        "workouts": ["created_at"],
        "workout_logs": ["start_time", "end_time"],
        "set_logs": ["completed_at"],
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
# EXERCISES
# ============================================================================

def get_all_exercises() -> pd.DataFrame:
    """Get all exercises"""
    return load_table("exercises")


def get_exercise_by_id(exercise_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single exercise by ID

    Args:
        exercise_id: Exercise ID

    Returns:
        Exercise dict or None if not found
    """
    df = load_table("exercises")
    result = df[df['id'] == exercise_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def create_exercise(
    name: str,
    description: str = "",
    primary_muscle_groups: str = "",
    secondary_muscle_groups: str = "",
    progression_scheme: str = "rep_range",
    rep_range_min: Optional[int] = None,
    rep_range_max: Optional[int] = None,
    target_reps: Optional[int] = None,
    rep_increment: Optional[int] = None,
    weight_increment: Optional[float] = None,
    warmup_config: Optional[str] = None
) -> int:
    """
    Create a new exercise

    Args:
        name: Exercise name
        description: Optional description
        primary_muscle_groups: Comma-separated muscle groups
        secondary_muscle_groups: Comma-separated muscle groups
        progression_scheme: Either "rep_range", "linear_weight", or "linear_reps"
        rep_range_min: Minimum reps for rep_range scheme
        rep_range_max: Maximum reps for rep_range scheme
        target_reps: Fixed/starting rep count for linear_weight or linear_reps scheme
        rep_increment: Rep increment for linear_reps scheme
        weight_increment: Weight increment in lbs/kg for rep_range and linear_weight schemes
        warmup_config: JSON string with warmup configuration

    Returns:
        New exercise ID
    """
    df = load_table("exercises")

    new_id = 1 if df.empty else int(df['id'].max() + 1)
    now = datetime.now()

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'description': description,
        'primary_muscle_groups': primary_muscle_groups,
        'secondary_muscle_groups': secondary_muscle_groups,
        'progression_scheme': progression_scheme,
        'rep_range_min': rep_range_min,
        'rep_range_max': rep_range_max,
        'target_reps': target_reps,
        'rep_increment': rep_increment,
        'weight_increment': weight_increment,
        'created_at': now,
        'warmup_config': warmup_config
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("exercises", df)

    return new_id


def update_exercise(
    exercise_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    primary_muscle_groups: Optional[str] = None,
    secondary_muscle_groups: Optional[str] = None,
    progression_scheme: Optional[str] = None,
    rep_range_min: Optional[int] = None,
    rep_range_max: Optional[int] = None,
    target_reps: Optional[int] = None,
    rep_increment: Optional[int] = None,
    weight_increment: Optional[float] = None,
    warmup_config: Optional[str] = None
) -> bool:
    """
    Update an existing exercise

    Args:
        exercise_id: Exercise ID to update
        name: Exercise name
        description: Optional description
        primary_muscle_groups: Comma-separated muscle groups
        secondary_muscle_groups: Comma-separated muscle groups
        progression_scheme: Either "rep_range", "linear_weight", or "linear_reps"
        rep_range_min: Minimum reps for rep_range scheme
        rep_range_max: Maximum reps for rep_range scheme
        target_reps: Fixed/starting rep count for linear_weight or linear_reps scheme
        rep_increment: Rep increment for linear_reps scheme
        weight_increment: Weight increment in lbs/kg for rep_range and linear_weight schemes
        warmup_config: JSON string with warmup configuration

    Returns:
        True if successful, False if exercise not found
    """
    df = load_table("exercises")
    mask = df['id'] == exercise_id

    if not mask.any():
        return False

    if name is not None:
        df.loc[mask, 'name'] = name
    if description is not None:
        df.loc[mask, 'description'] = description
    if primary_muscle_groups is not None:
        df.loc[mask, 'primary_muscle_groups'] = primary_muscle_groups
    if secondary_muscle_groups is not None:
        df.loc[mask, 'secondary_muscle_groups'] = secondary_muscle_groups
    if progression_scheme is not None:
        df.loc[mask, 'progression_scheme'] = progression_scheme
    if rep_range_min is not None:
        df.loc[mask, 'rep_range_min'] = rep_range_min
    if rep_range_max is not None:
        df.loc[mask, 'rep_range_max'] = rep_range_max
    if target_reps is not None:
        df.loc[mask, 'target_reps'] = target_reps
    if rep_increment is not None:
        df.loc[mask, 'rep_increment'] = rep_increment
    if weight_increment is not None:
        df.loc[mask, 'weight_increment'] = weight_increment
    if warmup_config is not None:
        df.loc[mask, 'warmup_config'] = warmup_config

    save_table("exercises", df)
    return True


# ============================================================================
# WORKOUTS
# ============================================================================

def get_all_workouts() -> pd.DataFrame:
    """Get all workouts"""
    return load_table("workouts")


def get_workout_by_id(workout_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single workout by ID

    Args:
        workout_id: Workout ID

    Returns:
        Workout dict or None if not found
    """
    df = load_table("workouts")
    result = df[df['id'] == workout_id]
    if result.empty:
        return None

    workout = result.iloc[0].to_dict()
    # Convert exercise_ids from comma-separated string to list
    if workout['exercise_ids']:
        workout['exercise_ids'] = [int(x.strip()) for x in str(workout['exercise_ids']).split(',')]
    else:
        workout['exercise_ids'] = []

    return workout


def create_workout(name: str, exercise_ids: List[int], notes: str = "") -> int:
    """
    Create a new workout template

    Args:
        name: Workout name
        exercise_ids: List of exercise IDs in order
        notes: Optional notes

    Returns:
        New workout ID
    """
    df = load_table("workouts")

    new_id = 1 if df.empty else int(df['id'].max() + 1)
    now = datetime.now()

    # Convert exercise_ids list to comma-separated string
    exercise_ids_str = ','.join(str(x) for x in exercise_ids)

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'exercise_ids': exercise_ids_str,
        'created_at': now,
        'notes': notes
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("workouts", df)

    return new_id


# ============================================================================
# WORKOUT LOGS
# ============================================================================

def get_all_workout_logs() -> pd.DataFrame:
    """Get all workout logs"""
    return load_table("workout_logs")


def get_workout_log_by_id(workout_log_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single workout log by ID

    Args:
        workout_log_id: Workout log ID

    Returns:
        Workout log dict or None if not found
    """
    df = load_table("workout_logs")
    result = df[df['id'] == workout_log_id]
    if result.empty:
        return None
    return result.iloc[0].to_dict()


def create_workout_log(workout_id: Optional[int] = None, start_time: datetime = None, status: str = "in_progress") -> int:
    """
    Create a new workout log entry

    Args:
        workout_id: Optional workout template ID (None for ad-hoc sets)
        start_time: Workout start timestamp
        status: Workout status (default: "in_progress")

    Returns:
        New workout log ID
    """
    df = load_table("workout_logs")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'workout_id': workout_id if workout_id is not None else None,
        'start_time': start_time,
        'end_time': None,
        'duration_seconds': None,
        'total_volume': None,
        'total_calories': None,
        'total_sets': None,
        'muscle_groups_trained': None,
        'status': status,
        'notes': None
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("workout_logs", df)

    return new_id


def update_workout_log(
    workout_log_id: int,
    end_time: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    total_volume: Optional[float] = None,
    total_calories: Optional[float] = None,
    total_sets: Optional[int] = None,
    muscle_groups_trained: Optional[str] = None,
    status: Optional[str] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update a workout log entry

    Args:
        workout_log_id: Workout log ID
        end_time: Workout end timestamp
        duration_seconds: Total workout duration
        total_volume: Total volume lifted
        total_calories: Total calories burned
        total_sets: Total sets completed
        muscle_groups_trained: Comma-separated muscle groups
        status: Workout status
        notes: Optional notes

    Returns:
        True if successful, False if not found
    """
    df = load_table("workout_logs")
    mask = df['id'] == workout_log_id

    if not mask.any():
        return False

    if end_time is not None:
        df.loc[mask, 'end_time'] = end_time
    if duration_seconds is not None:
        df.loc[mask, 'duration_seconds'] = duration_seconds
    if total_volume is not None:
        df.loc[mask, 'total_volume'] = total_volume
    if total_calories is not None:
        df.loc[mask, 'total_calories'] = total_calories
    if total_sets is not None:
        df.loc[mask, 'total_sets'] = total_sets
    if muscle_groups_trained is not None:
        df.loc[mask, 'muscle_groups_trained'] = muscle_groups_trained
    if status is not None:
        df.loc[mask, 'status'] = status
    if notes is not None:
        df.loc[mask, 'notes'] = notes

    save_table("workout_logs", df)
    return True


def query_workout_logs(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    workout_id: Optional[int] = None
) -> pd.DataFrame:
    """
    Query workout logs with filters

    Args:
        start_date: Filter by start date
        end_date: Filter by end date
        workout_id: Filter by workout template

    Returns:
        Filtered DataFrame of workout logs
    """
    df = load_table("workout_logs")

    if start_date is not None:
        df = df[df['start_time'] >= start_date]
    if end_date is not None:
        df = df[df['start_time'] <= end_date]
    if workout_id is not None:
        # Handle NULL/NaN values safely
        df = df[df['workout_id'].notna() & (df['workout_id'] == workout_id)]

    return df


# ============================================================================
# SET LOGS
# ============================================================================

def get_all_set_logs() -> pd.DataFrame:
    """Get all set logs"""
    return load_table("set_logs")


def get_set_logs_for_workout(workout_log_id: int) -> List[Dict[str, Any]]:
    """
    Get all set logs for a workout

    Args:
        workout_log_id: Workout log ID

    Returns:
        List of set log dicts
    """
    df = load_table("set_logs")
    sets = df[df['workout_log_id'] == workout_log_id]
    return sets.to_dict('records')


def create_set_log(
    workout_log_id: int,
    exercise_id: int,
    set_type: str,
    set_number: int,
    target_weight: float,
    target_reps: int,
    rest_seconds: int,
    completed: bool,
    actual_weight: Optional[float] = None,
    actual_reps: Optional[int] = None,
    completed_at: Optional[datetime] = None,
    one_rep_max_estimate: Optional[float] = None,
    volume: Optional[float] = None,
    duration_seconds: Optional[int] = None,
    calories: Optional[float] = None,
    notes: str = ""
) -> int:
    """
    Create a new set log entry

    Args:
        workout_log_id: Workout log ID
        exercise_id: Exercise ID
        set_type: Either "warmup" or "working"
        set_number: Set number within exercise
        target_weight: Prescribed weight
        target_reps: Prescribed reps
        rest_seconds: Rest time before this set
        completed: Whether set was completed
        actual_weight: Actual weight used (if different from target)
        actual_reps: Actual reps completed (if different from target)
        completed_at: Timestamp when set completed
        one_rep_max_estimate: Calculated 1RM
        volume: Weight × reps for this set
        duration_seconds: Time to complete set
        calories: Estimated calories
        notes: Optional notes

    Returns:
        New set log ID
    """
    df = load_table("set_logs")

    new_id = 1 if df.empty else int(df['id'].max() + 1)

    new_row = pd.DataFrame([{
        'id': new_id,
        'workout_log_id': workout_log_id,
        'exercise_id': exercise_id,
        'set_type': set_type,
        'set_number': set_number,
        'target_weight': target_weight,
        'actual_weight': actual_weight,
        'target_reps': target_reps,
        'actual_reps': actual_reps,
        'rest_seconds': rest_seconds,
        'completed': completed,
        'completed_at': completed_at,
        'one_rep_max_estimate': one_rep_max_estimate,
        'volume': volume,
        'duration_seconds': duration_seconds,
        'calories': calories,
        'notes': notes
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("set_logs", df)

    return new_id


# ============================================================================
# QUERY FUNCTIONS FOR HISTORY
# ============================================================================

def get_exercise_history(exercise_id: int) -> pd.DataFrame:
    """
    Get all set logs for an exercise, ordered by date

    Args:
        exercise_id: Exercise ID

    Returns:
        DataFrame of all sets for this exercise
    """
    df = load_table("set_logs")
    exercise_sets = df[df['exercise_id'] == exercise_id]

    if not exercise_sets.empty:
        exercise_sets = exercise_sets.sort_values('completed_at', ascending=False)

    return exercise_sets


def get_last_exercise_performance(exercise_id: int) -> Optional[Dict[str, Any]]:
    """
    Get the last completed performance data for an exercise

    Args:
        exercise_id: Exercise ID

    Returns:
        Dict with last workout data or None if no history
    """
    df = load_table("set_logs")

    # Filter for completed working sets only
    exercise_sets = df[
        (df['exercise_id'] == exercise_id) &
        (df['set_type'] == 'working') &
        (df['completed'] == True)
    ]

    if exercise_sets.empty:
        return None

    # Sort by completed_at and get most recent workout
    exercise_sets = exercise_sets.sort_values('completed_at', ascending=False)

    # Get the most recent workout_log_id
    last_workout_log_id = exercise_sets.iloc[0]['workout_log_id']

    # Get all sets from that workout for this exercise
    last_workout_sets = exercise_sets[exercise_sets['workout_log_id'] == last_workout_log_id]

    # Get the last working set from that workout
    last_set = last_workout_sets.iloc[0]

    return {
        'last_weight': last_set.get('actual_weight') or last_set['target_weight'],
        'last_reps': last_set.get('actual_reps') or last_set['target_reps'],
        'last_workout_date': last_set['completed_at'],
        'last_1rm': last_set['one_rep_max_estimate']
    }
