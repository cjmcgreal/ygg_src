"""
Progression engine and workout planning logic
All logic is framework-independent - no Streamlit dependencies
"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
import db
import analysis


def get_exercise_progression_data(exercise_id: int) -> Dict[str, Any]:
    """
    Query exercise history and extract progression data

    Args:
        exercise_id: Exercise ID

    Returns:
        Dict with last_weight, last_reps, all_working_sets_completed, has_history
    """
    set_logs = db.get_exercise_history(exercise_id)

    # Filter for completed working sets only
    working_sets = set_logs[
        (set_logs['set_type'] == 'working') &
        (set_logs['completed'] == True)
    ]

    if working_sets.empty:
        return {
            'has_history': False,
            'last_weight': None,
            'last_reps': None,
            'last_workout_date': None,
            'all_working_sets_completed': False
        }

    # Get most recent workout_log_id
    most_recent = working_sets.iloc[0]
    last_workout_log_id = most_recent['workout_log_id']

    # Get all working sets from that workout for this exercise
    last_workout_sets = working_sets[working_sets['workout_log_id'] == last_workout_log_id]

    # Convert to list of dicts for is_workout_successful
    sets_list = last_workout_sets.to_dict('records')

    # Determine if workout was successful
    all_completed = is_workout_successful(sets_list)

    # Get weight and reps from last set
    # For progression, we want the TARGET weight/reps (what was prescribed),
    # not necessarily what was achieved
    last_set = last_workout_sets.iloc[0]
    last_weight = last_set['target_weight']  # Use target weight
    last_reps = last_set['target_reps']  # Use target reps

    return {
        'has_history': True,
        'last_weight': float(last_weight),
        'last_reps': int(last_reps),
        'last_workout_date': last_set['completed_at'],
        'all_working_sets_completed': all_completed
    }


def is_workout_successful(set_logs: List[Dict]) -> bool:
    """
    Determine if all working sets completed with target reps or more

    Args:
        set_logs: List of set log dicts

    Returns:
        True if all working sets completed successfully
    """
    working_sets = [s for s in set_logs if s['set_type'] == 'working']

    if not working_sets:
        return False

    for s in working_sets:
        # Check if set was completed
        if not s.get('completed', False):
            return False

        # Check if actual reps >= target reps
        actual_reps = s.get('actual_reps') or s.get('target_reps', 0)
        target_reps = s.get('target_reps', 0)

        if actual_reps < target_reps:
            return False

    return True


def generate_warmup_sets(
    warmup_config: Dict[str, Any],
    working_weight: float,
    working_reps: int,
    one_rep_max: float
) -> List[Dict[str, Any]]:
    """
    Generate warmup sets based on working set intensity

    Args:
        warmup_config: Warmup configuration dict
        working_weight: Weight for working sets
        working_reps: Reps for working sets
        one_rep_max: Current estimated 1RM

    Returns:
        List of warmup set dicts
    """
    if not warmup_config or not warmup_config.get('enabled', False):
        return []

    # Calculate working set intensity as % of 1RM
    if one_rep_max and one_rep_max > 0:
        percent_1rm = (working_weight / one_rep_max) * 100
    else:
        # If no 1RM available, assume moderate intensity
        percent_1rm = 70.0

    # Determine number of warmup sets based on intensity
    warmup_count = 1  # Default
    for threshold in warmup_config['intensity_thresholds']:
        min_pct = threshold['min_percent_1rm']
        max_pct = threshold['max_percent_1rm']

        if min_pct <= percent_1rm < max_pct:
            warmup_count = threshold['warmup_sets']
            break

    # Generate warmup sets
    warmup_sets = []
    warmup_percentages = warmup_config['warmup_percentages'][:warmup_count]
    warmup_reps = warmup_config['warmup_reps'][:warmup_count]

    for i, (percent, reps) in enumerate(zip(warmup_percentages, warmup_reps)):
        warmup_weight = working_weight * (percent / 100)

        # Round to nearest 5 lbs for practicality
        warmup_weight = round(warmup_weight / 5) * 5

        warmup_sets.append({
            'set_type': 'warmup',
            'set_number': i + 1,
            'target_weight': warmup_weight,
            'target_reps': reps,
            'rest_seconds': 60  # Shorter rest for warmups
        })

    return warmup_sets


def calculate_next_workout_sets(
    exercise_id: int,
    workout_log_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Calculate next workout sets based on progression logic

    Args:
        exercise_id: Exercise ID
        workout_log_id: Optional workout log ID (for future use)

    Returns:
        List of set dicts (warmup + working sets)
    """
    # Load exercise configuration
    exercise = db.get_exercise_by_id(exercise_id)
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    # Get exercise history
    history = get_exercise_progression_data(exercise_id)

    # Get current 1RM estimate
    current_1rm = analysis.get_latest_one_rep_max(exercise_id)

    # Determine next weight and reps based on progression scheme
    progression_scheme = exercise['progression_scheme']

    if progression_scheme == 'rep_range':
        next_weight, next_reps = _calculate_rep_range_progression(exercise, history)
    elif progression_scheme == 'linear_weight':
        next_weight, next_reps = _calculate_linear_weight_progression(exercise, history)
    else:
        raise ValueError(f"Unknown progression scheme: {progression_scheme}")

    # Generate working sets (default: 3 sets)
    working_sets = []
    for i in range(3):
        working_sets.append({
            'set_type': 'working',
            'set_number': i + 1,
            'target_weight': next_weight,
            'target_reps': next_reps,
            'rest_seconds': 120  # Default rest for working sets
        })

    # Generate warmup sets if enabled
    warmup_sets = []
    warmup_config_str = exercise.get('warmup_config')

    # Check if warmup_config is not None and not NaN
    if warmup_config_str and not pd.isna(warmup_config_str):
        try:
            warmup_config = json.loads(warmup_config_str)
            warmup_sets = generate_warmup_sets(
                warmup_config,
                next_weight,
                next_reps,
                current_1rm
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            # If warmup config is invalid, skip warmups
            pass

    # Combine warmup + working sets
    all_sets = warmup_sets + working_sets

    return all_sets


def _calculate_rep_range_progression(
    exercise: Dict[str, Any],
    history: Dict[str, Any]
) -> tuple[float, int]:
    """
    Calculate next weight and reps for rep range progression

    Args:
        exercise: Exercise configuration dict
        history: Exercise progression data

    Returns:
        Tuple of (next_weight, next_reps)
    """
    rep_min = exercise['rep_range_min']
    rep_max = exercise['rep_range_max']
    weight_increment = exercise['weight_increment']

    # First workout - use default starting weight
    if not history['has_history']:
        return (45.0, int(rep_min))  # Start with bar weight

    last_weight = history['last_weight']
    last_reps = history['last_reps']
    was_successful = history['all_working_sets_completed']

    if was_successful:
        # Successful workout
        if last_reps < rep_max:
            # Still room to add reps
            next_reps = last_reps + 1
            next_weight = last_weight
        else:
            # Hit top of rep range, add weight and reset to min
            next_reps = int(rep_min)
            next_weight = last_weight + weight_increment
    else:
        # Failed workout, repeat same parameters
        next_reps = last_reps
        next_weight = last_weight

    return (next_weight, next_reps)


def _calculate_linear_weight_progression(
    exercise: Dict[str, Any],
    history: Dict[str, Any]
) -> tuple[float, int]:
    """
    Calculate next weight and reps for linear weight progression

    Args:
        exercise: Exercise configuration dict
        history: Exercise progression data

    Returns:
        Tuple of (next_weight, next_reps)
    """
    target_reps = exercise['target_reps']
    weight_increment = exercise['weight_increment']

    # Reps always constant
    next_reps = int(target_reps)

    # First workout - use default starting weight
    if not history['has_history']:
        return (45.0, next_reps)  # Start with bar weight

    last_weight = history['last_weight']
    was_successful = history['all_working_sets_completed']

    if was_successful:
        # Successful workout, add weight
        next_weight = last_weight + weight_increment
    else:
        # Failed workout, repeat weight
        next_weight = last_weight

    return (next_weight, next_reps)
