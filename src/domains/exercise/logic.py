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

    Supports both reps-based and duration-based exercises.

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

    exercise_type = exercise.get('exercise_type', 'reps')

    # Handle duration-based exercises
    if exercise_type == 'duration':
        target_duration = _calculate_duration_progression(exercise, history)
        return [{
            'set_type': 'working',
            'set_number': 1,
            'target_weight': 0,
            'target_reps': 1,  # 1 "rep" = 1 hold
            'target_duration': target_duration,
            'rest_seconds': 60
        }]

    # Reps-based exercise handling
    # Get current 1RM estimate
    current_1rm = analysis.get_latest_one_rep_max(exercise_id)

    # Determine next weight and reps based on progression scheme
    progression_scheme = exercise['progression_scheme']

    if progression_scheme == 'rep_range':
        next_weight, next_reps = _calculate_rep_range_progression(exercise, history)
    elif progression_scheme == 'linear_weight':
        next_weight, next_reps = _calculate_linear_weight_progression(exercise, history)
    elif progression_scheme == 'linear_reps':
        next_weight, next_reps = _calculate_linear_reps_progression(exercise, history)
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

    # Check if warmup is required (use new boolean flag, fall back to legacy JSON)
    warmup_required = exercise.get('warmup_required')
    if pd.isna(warmup_required):
        # Fall back to legacy warmup_config JSON
        warmup_config_str = exercise.get('warmup_config')
        if warmup_config_str and not pd.isna(warmup_config_str):
            try:
                warmup_config = json.loads(warmup_config_str)
                warmup_required = warmup_config.get('enabled', False)
            except (json.JSONDecodeError, KeyError, TypeError):
                warmup_required = True
        else:
            warmup_required = True

    # Generate warmup sets if required
    warmup_sets = []
    if warmup_required:
        default_warmup_config = {
            'enabled': True,
            'intensity_thresholds': [
                {'min_percent_1rm': 0, 'max_percent_1rm': 50, 'warmup_sets': 1},
                {'min_percent_1rm': 50, 'max_percent_1rm': 70, 'warmup_sets': 2},
                {'min_percent_1rm': 70, 'max_percent_1rm': 100, 'warmup_sets': 3}
            ],
            'warmup_percentages': [40, 60, 80],
            'warmup_reps': [8, 6, 4]
        }
        warmup_sets = generate_warmup_sets(
            default_warmup_config,
            next_weight,
            next_reps,
            current_1rm
        )

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


def _calculate_linear_reps_progression(
    exercise: Dict[str, Any],
    history: Dict[str, Any]
) -> tuple[float, int]:
    """
    Calculate next weight and reps for linear reps progression

    Weight stays constant, reps increase by rep_increment each successful workout.

    Args:
        exercise: Exercise configuration dict
        history: Exercise progression data

    Returns:
        Tuple of (next_weight, next_reps)
    """
    target_reps = exercise['target_reps']  # Starting reps
    rep_increment = exercise['rep_increment']

    # First workout - use starting reps and default weight
    if not history['has_history']:
        return (45.0, int(target_reps))  # Start with bar weight and starting reps

    last_weight = history['last_weight']
    last_reps = history['last_reps']
    was_successful = history['all_working_sets_completed']

    # Weight stays the same
    next_weight = last_weight

    if was_successful:
        # Successful workout, add reps
        next_reps = last_reps + rep_increment
    else:
        # Failed workout, repeat same reps
        next_reps = last_reps

    return (next_weight, next_reps)


def _calculate_duration_progression(
    exercise: Dict[str, Any],
    history: Dict[str, Any]
) -> int:
    """
    Calculate next target duration for duration-based exercises

    Duration increases by duration_increment each successful workout.

    Args:
        exercise: Exercise configuration dict
        history: Exercise progression data (last_duration in 'last_reps' field)

    Returns:
        Next target duration in seconds
    """
    target_duration = exercise.get('target_duration', 30)  # Default 30 seconds
    duration_increment = exercise.get('duration_increment', 5)  # Default +5 seconds

    # First workout - use starting duration
    if not history['has_history']:
        return int(target_duration) if target_duration else 30

    # For duration exercises, we store duration in the 'last_reps' field
    last_duration = history.get('last_reps', target_duration)
    was_successful = history['all_working_sets_completed']

    if was_successful:
        # Successful workout, add duration
        next_duration = last_duration + (duration_increment or 5)
    else:
        # Failed workout, repeat same duration
        next_duration = last_duration

    return int(next_duration)


def calculate_next_duration(exercise_id: int) -> int:
    """
    Calculate next target duration for a duration-based exercise

    Args:
        exercise_id: Exercise ID

    Returns:
        Next target duration in seconds
    """
    exercise = db.get_exercise_by_id(exercise_id)
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    if exercise.get('exercise_type') != 'duration':
        raise ValueError(f"Exercise {exercise_id} is not a duration-based exercise")

    history = get_exercise_progression_data(exercise_id)
    return _calculate_duration_progression(exercise, history)


# ============================================================================
# INTENSITY-BASED CALCULATIONS (for slot-based templates)
# ============================================================================

# Intensity category definitions
INTENSITY_RANGES = {
    'strength': (3, 6),      # Heavy weight, low reps
    'hypertrophy': (7, 11),  # Moderate weight, medium reps
    'endurance': (12, 15)    # Light weight, high reps
}

# Approximate %1RM for different rep ranges (Epley/Brzycki derived)
INTENSITY_1RM_PERCENT = {
    'strength': 0.85,      # ~85% 1RM for 3-6 reps
    'hypertrophy': 0.70,   # ~70% 1RM for 7-11 reps
    'endurance': 0.60      # ~60% 1RM for 12-15 reps
}


def get_rep_range_for_intensity(intensity: str) -> tuple:
    """
    Get the rep range (min, max) for a given intensity category

    Args:
        intensity: 'strength', 'hypertrophy', or 'endurance'

    Returns:
        Tuple of (min_reps, max_reps)
    """
    return INTENSITY_RANGES.get(intensity.lower(), (8, 12))


def calculate_weight_for_intensity(exercise_id: int, intensity: str) -> float:
    """
    Calculate appropriate working weight based on intensity and exercise 1RM

    Uses the exercise's historical 1RM to determine appropriate weight for
    the given intensity level. Falls back to starting weight if no history.

    Args:
        exercise_id: Exercise ID
        intensity: 'strength', 'hypertrophy', or 'endurance'

    Returns:
        Recommended weight in lbs, rounded to nearest 5
    """
    # Get current 1RM estimate
    current_1rm = analysis.get_latest_one_rep_max(exercise_id)

    if current_1rm and current_1rm > 0:
        # Calculate weight from %1RM
        percent = INTENSITY_1RM_PERCENT.get(intensity.lower(), 0.70)
        calculated_weight = current_1rm * percent

        # Round to nearest 5 lbs for practicality
        return round(calculated_weight / 5) * 5
    else:
        # No history - return starting weight (bar only)
        return 45.0


def generate_sets_for_slot(
    exercise_id: int,
    intensity: str,
    num_sets: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate complete set list (warmup + working) for a slot-based exercise

    Supports both reps-based and duration-based exercises.

    Args:
        exercise_id: Exercise ID
        intensity: 'strength', 'hypertrophy', or 'endurance'
        num_sets: Number of working sets to generate (default: 3)

    Returns:
        List of set dicts with set_type, set_number, target_weight, target_reps/target_duration
    """
    # Get exercise configuration
    exercise = db.get_exercise_by_id(exercise_id)
    if not exercise:
        raise ValueError(f"Exercise {exercise_id} not found")

    exercise_type = exercise.get('exercise_type', 'reps')

    # Handle duration-based exercises (no warmup, single set with duration)
    if exercise_type == 'duration':
        target_duration = _calculate_duration_progression(
            exercise,
            get_exercise_progression_data(exercise_id)
        )
        # Duration exercises typically have 1 "set" that's held for duration
        return [{
            'set_type': 'working',
            'set_number': 1,
            'target_weight': 0,
            'target_reps': 1,  # 1 "rep" = 1 hold
            'target_duration': target_duration,
            'rest_seconds': 60
        }]

    # Reps-based exercise handling
    # Get rep range for this intensity
    rep_min, rep_max = get_rep_range_for_intensity(intensity)

    # Start at low end of rep range for new sessions
    target_reps = rep_min

    # Calculate working weight for this intensity
    working_weight = calculate_weight_for_intensity(exercise_id, intensity)

    # Get current 1RM for warmup calculations
    current_1rm = analysis.get_latest_one_rep_max(exercise_id)

    # Check if warmup is required (use new boolean flag, fall back to legacy JSON)
    warmup_required = exercise.get('warmup_required')
    if pd.isna(warmup_required):
        # Fall back to legacy warmup_config JSON
        warmup_config_str = exercise.get('warmup_config')
        if warmup_config_str and not pd.isna(warmup_config_str):
            try:
                warmup_config = json.loads(warmup_config_str)
                warmup_required = warmup_config.get('enabled', False)
            except (json.JSONDecodeError, KeyError, TypeError):
                warmup_required = True  # Default to True for reps-based
        else:
            warmup_required = True  # Default to True for reps-based

    # Generate warmup sets if required
    warmup_sets = []
    if warmup_required:
        # Use default warmup config
        default_warmup_config = {
            'enabled': True,
            'intensity_thresholds': [
                {'min_percent_1rm': 0, 'max_percent_1rm': 50, 'warmup_sets': 1},
                {'min_percent_1rm': 50, 'max_percent_1rm': 70, 'warmup_sets': 2},
                {'min_percent_1rm': 70, 'max_percent_1rm': 100, 'warmup_sets': 3}
            ],
            'warmup_percentages': [40, 60, 80],
            'warmup_reps': [8, 6, 4]
        }
        warmup_sets = generate_warmup_sets(
            default_warmup_config,
            working_weight,
            target_reps,
            current_1rm or 0
        )

    # Generate working sets
    working_sets = []
    for i in range(num_sets):
        working_sets.append({
            'set_type': 'working',
            'set_number': i + 1,
            'target_weight': working_weight,
            'target_reps': target_reps,
            'rest_seconds': 120  # Default rest for working sets
        })

    return warmup_sets + working_sets


def get_intensity_label(intensity: str) -> str:
    """
    Get human-readable label for intensity category

    Args:
        intensity: 'strength', 'hypertrophy', or 'endurance'

    Returns:
        Formatted label string with rep range
    """
    rep_min, rep_max = get_rep_range_for_intensity(intensity)
    labels = {
        'strength': f'Strength ({rep_min}-{rep_max} reps)',
        'hypertrophy': f'Hypertrophy ({rep_min}-{rep_max} reps)',
        'endurance': f'Endurance ({rep_min}-{rep_max} reps)'
    }
    return labels.get(intensity.lower(), f'Unknown ({rep_min}-{rep_max} reps)')
