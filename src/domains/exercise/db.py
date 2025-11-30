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
            "id", "name", "variant", "description", "primary_muscle_groups",
            "secondary_muscle_groups", "progression_scheme",
            "rep_range_min", "rep_range_max", "target_reps",
            "rep_increment", "weight_increment", "created_at", "warmup_config",
            # Exercise type and duration fields
            "exercise_type",     # "reps" or "duration"
            "target_duration",   # Target duration in seconds (for duration type)
            "duration_increment", # Seconds to add per workout (for duration type)
            "warmup_required",   # Boolean - whether to generate warmup sets
            # PR tracking fields
            "observed_1rm",      # Auto-calculated from history (max weight where reps=1)
            "estimated_1rm",     # Calculated from sets using Epley formula
            "max_set_volume",    # Best single set (weight × reps)
            "max_exercise_volume" # Best total volume in one workout session
        ],
        "workouts": [
            "id", "name", "exercise_ids", "created_at", "notes"
        ],
        "workout_templates": [
            "id", "name", "label", "slot_definitions", "created_at", "notes"
        ],
        "workout_cycle_state": [
            "id", "active_labels", "current_index", "updated_at"
        ],
        "exercise_selections": [
            "id", "template_id", "slot_order", "exercise_id", "selected_at"
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
        "workout_templates": ["created_at"],
        "workout_cycle_state": ["updated_at"],
        "exercise_selections": ["selected_at"],
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


# Available exercise variants
EXERCISE_VARIANTS = [
    "barbell",
    "dumbbell",
    "machine",
    "cable",
    "bodyweight",
    "kettlebell",
    "bands",
    "other"
]


def create_exercise(
    name: str,
    variant: str = "barbell",
    description: str = "",
    primary_muscle_groups: str = "",
    secondary_muscle_groups: str = "",
    progression_scheme: str = "rep_range",
    rep_range_min: Optional[int] = None,
    rep_range_max: Optional[int] = None,
    target_reps: Optional[int] = None,
    rep_increment: Optional[int] = None,
    weight_increment: Optional[float] = None,
    warmup_config: Optional[str] = None,
    exercise_type: str = "reps",
    target_duration: Optional[int] = None,
    duration_increment: Optional[int] = None,
    warmup_required: bool = True
) -> int:
    """
    Create a new exercise

    Args:
        name: Exercise name (e.g., "Bench Press", "Chest Press")
        variant: Equipment variant (barbell, dumbbell, machine, cable, etc.)
        description: Optional description
        primary_muscle_groups: Comma-separated muscle groups
        secondary_muscle_groups: Comma-separated muscle groups
        progression_scheme: Either "rep_range", "linear_weight", "linear_reps", or "duration"
        rep_range_min: Minimum reps for rep_range scheme
        rep_range_max: Maximum reps for rep_range scheme
        target_reps: Fixed/starting rep count for linear_weight or linear_reps scheme
        rep_increment: Rep increment for linear_reps scheme
        weight_increment: Weight increment in lbs/kg for rep_range and linear_weight schemes
        warmup_config: JSON string with warmup configuration (legacy, prefer warmup_required)
        exercise_type: "reps" or "duration"
        target_duration: Target duration in seconds (for duration type)
        duration_increment: Seconds to add per workout (for duration type)
        warmup_required: Whether to generate warmup sets (default: True)

    Returns:
        New exercise ID
    """
    df = load_table("exercises")

    new_id = 1 if df.empty else int(df['id'].max() + 1)
    now = datetime.now()

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'variant': variant.lower(),
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
        'warmup_config': warmup_config,
        'exercise_type': exercise_type,
        'target_duration': target_duration,
        'duration_increment': duration_increment,
        'warmup_required': warmup_required,
        'observed_1rm': None,  # Auto-calculated from history
        'estimated_1rm': None,
        'max_set_volume': None,
        'max_exercise_volume': None
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("exercises", df)

    return new_id


def update_exercise(
    exercise_id: int,
    name: Optional[str] = None,
    variant: Optional[str] = None,
    description: Optional[str] = None,
    primary_muscle_groups: Optional[str] = None,
    secondary_muscle_groups: Optional[str] = None,
    progression_scheme: Optional[str] = None,
    rep_range_min: Optional[int] = None,
    rep_range_max: Optional[int] = None,
    target_reps: Optional[int] = None,
    rep_increment: Optional[int] = None,
    weight_increment: Optional[float] = None,
    warmup_config: Optional[str] = None,
    exercise_type: Optional[str] = None,
    target_duration: Optional[int] = None,
    duration_increment: Optional[int] = None,
    warmup_required: Optional[bool] = None
) -> bool:
    """
    Update an existing exercise

    Args:
        exercise_id: Exercise ID to update
        name: Exercise name
        variant: Equipment variant (barbell, dumbbell, machine, cable, etc.)
        description: Optional description
        primary_muscle_groups: Comma-separated muscle groups
        secondary_muscle_groups: Comma-separated muscle groups
        progression_scheme: Either "rep_range", "linear_weight", "linear_reps", or "duration"
        rep_range_min: Minimum reps for rep_range scheme
        rep_range_max: Maximum reps for rep_range scheme
        target_reps: Fixed/starting rep count for linear_weight or linear_reps scheme
        rep_increment: Rep increment for linear_reps scheme
        weight_increment: Weight increment in lbs/kg for rep_range and linear_weight schemes
        warmup_config: JSON string with warmup configuration (legacy)
        exercise_type: "reps" or "duration"
        target_duration: Target duration in seconds (for duration type)
        duration_increment: Seconds to add per workout (for duration type)
        warmup_required: Whether to generate warmup sets

    Returns:
        True if successful, False if exercise not found
    """
    df = load_table("exercises")
    mask = df['id'] == exercise_id

    if not mask.any():
        return False

    if name is not None:
        df.loc[mask, 'name'] = name
    if variant is not None:
        df.loc[mask, 'variant'] = variant.lower()
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
    if exercise_type is not None:
        df.loc[mask, 'exercise_type'] = exercise_type
    if target_duration is not None:
        df.loc[mask, 'target_duration'] = target_duration
    if duration_increment is not None:
        df.loc[mask, 'duration_increment'] = duration_increment
    if warmup_required is not None:
        df.loc[mask, 'warmup_required'] = warmup_required

    save_table("exercises", df)
    return True


def update_exercise_prs(
    exercise_id: int,
    observed_1rm: Optional[float] = None,
    estimated_1rm: Optional[float] = None,
    max_set_volume: Optional[float] = None,
    max_exercise_volume: Optional[float] = None
) -> bool:
    """
    Update exercise PR fields (called after workout completion)

    Only updates if new value is greater than existing (true PR).

    Args:
        exercise_id: Exercise ID
        observed_1rm: New observed 1RM (max weight where reps=1 from history)
        estimated_1rm: New estimated 1RM from workout
        max_set_volume: New max set volume (if PR)
        max_exercise_volume: New max exercise volume (if PR)

    Returns:
        True if any PR was updated
    """
    df = load_table("exercises")
    mask = df['id'] == exercise_id

    if not mask.any():
        return False

    updated = False
    current = df.loc[mask].iloc[0]

    # Update observed_1rm if greater than current
    if observed_1rm is not None:
        current_obs = current.get('observed_1rm')
        if pd.isna(current_obs) or observed_1rm > current_obs:
            df.loc[mask, 'observed_1rm'] = observed_1rm
            updated = True

    # Update estimated_1rm if greater than current
    if estimated_1rm is not None:
        current_1rm = current.get('estimated_1rm')
        if pd.isna(current_1rm) or estimated_1rm > current_1rm:
            df.loc[mask, 'estimated_1rm'] = estimated_1rm
            updated = True

    # Update max_set_volume if greater than current
    if max_set_volume is not None:
        current_set_vol = current.get('max_set_volume')
        if pd.isna(current_set_vol) or max_set_volume > current_set_vol:
            df.loc[mask, 'max_set_volume'] = max_set_volume
            updated = True

    # Update max_exercise_volume if greater than current
    if max_exercise_volume is not None:
        current_ex_vol = current.get('max_exercise_volume')
        if pd.isna(current_ex_vol) or max_exercise_volume > current_ex_vol:
            df.loc[mask, 'max_exercise_volume'] = max_exercise_volume
            updated = True

    if updated:
        save_table("exercises", df)

    return updated


def calculate_observed_1rm_from_history(exercise_id: int) -> Optional[float]:
    """
    Calculate observed 1RM from exercise history.

    Finds the heaviest weight where actual_reps = 1 from completed set logs.

    Args:
        exercise_id: Exercise ID

    Returns:
        Max weight lifted for a single rep, or None if no single-rep sets found
    """
    set_logs_df = load_table("set_logs")

    if set_logs_df.empty:
        return None

    # Filter for this exercise, completed sets, working sets only, reps = 1
    mask = (
        (set_logs_df['exercise_id'] == exercise_id) &
        (set_logs_df['completed'] == True) &
        (set_logs_df['set_type'] == 'working')
    )
    exercise_sets = set_logs_df[mask]

    if exercise_sets.empty:
        return None

    # Check actual_reps first, fall back to target_reps if actual is null
    single_rep_sets = []
    for _, row in exercise_sets.iterrows():
        actual_reps = row.get('actual_reps')
        if pd.isna(actual_reps):
            actual_reps = row.get('target_reps')

        if actual_reps == 1:
            actual_weight = row.get('actual_weight')
            if pd.isna(actual_weight):
                actual_weight = row.get('target_weight')
            if actual_weight and actual_weight > 0:
                single_rep_sets.append(actual_weight)

    if not single_rep_sets:
        return None

    return max(single_rep_sets)


def get_exercise_display_name(exercise: Dict[str, Any]) -> str:
    """
    Get formatted display name for an exercise including variant

    Args:
        exercise: Exercise dict

    Returns:
        Formatted string like "Barbell Bench Press" or "Machine Chest Press"
    """
    variant = exercise.get('variant', '')
    name = exercise.get('name', 'Unknown')

    if variant and variant != 'other':
        return f"{variant.title()} {name}"
    return name


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
# WORKOUT TEMPLATES (slot-based)
# ============================================================================

def get_all_workout_templates() -> pd.DataFrame:
    """Get all workout templates"""
    return load_table("workout_templates")


def get_workout_template_by_id(template_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single workout template by ID

    Args:
        template_id: Template ID

    Returns:
        Template dict or None if not found
    """
    df = load_table("workout_templates")
    result = df[df['id'] == template_id]
    if result.empty:
        return None

    template = result.iloc[0].to_dict()
    # Parse slot_definitions from JSON string
    import json
    if template.get('slot_definitions'):
        try:
            template['slot_definitions'] = json.loads(template['slot_definitions'])
        except (json.JSONDecodeError, TypeError):
            template['slot_definitions'] = []
    else:
        template['slot_definitions'] = []

    return template


def get_workout_template_by_label(label: str) -> Optional[Dict[str, Any]]:
    """
    Get a workout template by its label (A, B, C, etc.)

    Args:
        label: Single letter label

    Returns:
        Template dict or None if not found
    """
    df = load_table("workout_templates")
    result = df[df['label'] == label.upper()]
    if result.empty:
        return None

    template = result.iloc[0].to_dict()
    # Parse slot_definitions from JSON string
    import json
    if template.get('slot_definitions'):
        try:
            template['slot_definitions'] = json.loads(template['slot_definitions'])
        except (json.JSONDecodeError, TypeError):
            template['slot_definitions'] = []
    else:
        template['slot_definitions'] = []

    return template


def create_workout_template(
    name: str,
    label: str,
    slot_definitions: List[Dict[str, Any]],
    notes: str = ""
) -> int:
    """
    Create a new workout template with slot definitions

    Args:
        name: Template name (e.g., "Push Day")
        label: Single letter label (A, B, C, etc.)
        slot_definitions: List of slot dicts with muscle_group, intensity, sets
        notes: Optional notes

    Returns:
        New template ID
    """
    import json
    df = load_table("workout_templates")

    new_id = 1 if df.empty else int(df['id'].max() + 1)
    now = datetime.now()

    # Convert slot_definitions to JSON string
    slot_json = json.dumps(slot_definitions)

    new_row = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'label': label.upper(),
        'slot_definitions': slot_json,
        'created_at': now,
        'notes': notes
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    save_table("workout_templates", df)

    return new_id


def update_workout_template(
    template_id: int,
    name: Optional[str] = None,
    label: Optional[str] = None,
    slot_definitions: Optional[List[Dict[str, Any]]] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Update an existing workout template

    Args:
        template_id: Template ID to update
        name: Template name
        label: Single letter label
        slot_definitions: List of slot dicts
        notes: Optional notes

    Returns:
        True if successful, False if template not found
    """
    import json
    df = load_table("workout_templates")
    mask = df['id'] == template_id

    if not mask.any():
        return False

    if name is not None:
        df.loc[mask, 'name'] = name
    if label is not None:
        df.loc[mask, 'label'] = label.upper()
    if slot_definitions is not None:
        df.loc[mask, 'slot_definitions'] = json.dumps(slot_definitions)
    if notes is not None:
        df.loc[mask, 'notes'] = notes

    save_table("workout_templates", df)
    return True


def delete_workout_template(template_id: int) -> bool:
    """
    Delete a workout template

    Args:
        template_id: Template ID to delete

    Returns:
        True if successful, False if template not found
    """
    df = load_table("workout_templates")
    mask = df['id'] == template_id

    if not mask.any():
        return False

    df = df[~mask]
    save_table("workout_templates", df)
    return True


# ============================================================================
# WORKOUT CYCLE STATE
# ============================================================================

def get_cycle_state() -> Dict[str, Any]:
    """
    Get the current workout cycle state (singleton)

    Returns:
        Dict with active_labels, current_index, updated_at
        Creates default if not exists
    """
    df = load_table("workout_cycle_state")

    if df.empty:
        # Create default state with all templates active
        templates_df = load_table("workout_templates")
        if templates_df.empty:
            active_labels = ""
        else:
            active_labels = ",".join(templates_df['label'].dropna().unique())

        return {
            'id': 1,
            'active_labels': active_labels,
            'current_index': 0,
            'updated_at': None
        }

    state = df.iloc[0].to_dict()
    return state


def update_cycle_state(
    active_labels: Optional[str] = None,
    current_index: Optional[int] = None
) -> bool:
    """
    Update the workout cycle state

    Args:
        active_labels: Comma-separated active workout labels
        current_index: Current position in rotation

    Returns:
        True if successful
    """
    df = load_table("workout_cycle_state")
    now = datetime.now()

    if df.empty:
        # Create new state
        new_row = pd.DataFrame([{
            'id': 1,
            'active_labels': active_labels or "",
            'current_index': current_index or 0,
            'updated_at': now
        }])
        save_table("workout_cycle_state", new_row)
        return True

    # Update existing state
    if active_labels is not None:
        df.loc[0, 'active_labels'] = active_labels
    if current_index is not None:
        df.loc[0, 'current_index'] = current_index
    df.loc[0, 'updated_at'] = now

    save_table("workout_cycle_state", df)
    return True


def advance_cycle() -> Dict[str, Any]:
    """
    Advance to the next workout in the cycle

    Returns:
        Updated cycle state with new current workout
    """
    state = get_cycle_state()
    active_labels = state.get('active_labels', '')

    if not active_labels:
        return state

    labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]
    if not labels_list:
        return state

    current_index = state.get('current_index', 0)
    new_index = (current_index + 1) % len(labels_list)

    update_cycle_state(current_index=new_index)

    return {
        'id': 1,
        'active_labels': active_labels,
        'current_index': new_index,
        'updated_at': datetime.now(),
        'current_label': labels_list[new_index]
    }


def get_current_workout_label() -> Optional[str]:
    """
    Get the current workout label from cycle state

    Returns:
        Current workout label (A, B, C, etc.) or None if no workouts configured
    """
    state = get_cycle_state()
    active_labels = state.get('active_labels', '')

    if not active_labels:
        return None

    labels_list = [l.strip() for l in active_labels.split(',') if l.strip()]
    if not labels_list:
        return None

    current_index = state.get('current_index', 0)
    # Ensure index is within bounds
    if current_index >= len(labels_list):
        current_index = 0

    return labels_list[current_index]


# ============================================================================
# EXERCISE SELECTIONS (mapping exercises to template slots)
# ============================================================================

def get_selections_for_template(template_id: int) -> List[Dict[str, Any]]:
    """
    Get all exercise selections for a template

    Args:
        template_id: Template ID

    Returns:
        List of selection dicts with slot_order and exercise_id
    """
    df = load_table("exercise_selections")
    selections = df[df['template_id'] == template_id]
    return selections.to_dict('records')


def set_exercise_for_slot(
    template_id: int,
    slot_order: int,
    exercise_id: int
) -> int:
    """
    Set or update the exercise for a template slot

    Args:
        template_id: Template ID
        slot_order: Slot position in template
        exercise_id: Exercise ID to assign

    Returns:
        Selection ID
    """
    df = load_table("exercise_selections")
    now = datetime.now()

    # Check if selection already exists
    mask = (df['template_id'] == template_id) & (df['slot_order'] == slot_order)

    if mask.any():
        # Update existing selection
        df.loc[mask, 'exercise_id'] = exercise_id
        df.loc[mask, 'selected_at'] = now
        save_table("exercise_selections", df)
        return int(df.loc[mask, 'id'].iloc[0])
    else:
        # Create new selection
        new_id = 1 if df.empty else int(df['id'].max() + 1)

        new_row = pd.DataFrame([{
            'id': new_id,
            'template_id': template_id,
            'slot_order': slot_order,
            'exercise_id': exercise_id,
            'selected_at': now
        }])

        df = pd.concat([df, new_row], ignore_index=True)
        save_table("exercise_selections", df)
        return new_id


def clear_selections_for_template(template_id: int) -> bool:
    """
    Clear all exercise selections for a template

    Args:
        template_id: Template ID

    Returns:
        True if any selections were deleted
    """
    df = load_table("exercise_selections")
    mask = df['template_id'] == template_id

    if not mask.any():
        return False

    df = df[~mask]
    save_table("exercise_selections", df)
    return True


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
